use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;
use std::path::Path;
use colored::Colorize;
use std::process::Command;
use git2::{Repository, Signature};
use anyhow::Result;

pub struct DepResolver {
    available_deps: HashSet<String>,
    lib_map: HashMap<String, String>,
    lib_versions: HashMap<String, String>,
}

impl DepResolver {
    pub fn new() -> Self {
        let mut available_deps = HashSet::new();
        available_deps.insert("std".to_string());
        available_deps.insert("math".to_string());
        available_deps.insert("io".to_string());

        let mut lib_map = HashMap::new();
        let mut lib_versions = HashMap::new();
        let temp_dir = env::temp_dir();
        let lib_file = temp_dir.join("library.weave");
        let fetch_url = "https://raw.githubusercontent.com/Velvet-Lang/velvet/main/weave/library.weave";
        if cfg!(target_os = "windows") {
            Command::new("powershell")
                .args(&["Invoke-WebRequest", "-Uri", fetch_url, "-OutFile", lib_file.to_str().unwrap()])
                .status().ok();
        } else {
            Command::new("curl").args(&["-o", lib_file.to_str().unwrap(), fetch_url]).status().ok();
        }
        let content = fs::read_to_string(&lib_file).unwrap_or_default();
        for line in content.lines() {
            let parts: Vec<&str> = line.split(" > ").collect();
            if parts.len() == 2 {
                let name_parts: Vec<&str> = parts[0].split('@').collect();
                let name = name_parts[0].trim().to_string();
                let ver = if name_parts.len() > 1 { name_parts[1].to_string() } else { String::new() };
                lib_map.insert(name.clone(), parts[1].trim().to_string());
                if !ver.is_empty() {
                    lib_versions.insert(name, ver);
                }
            }
        }
        // Fallback
        lib_map.insert("crich-cli".to_string(), "https://github.com/Velvet-Lang/crich-cli.git".to_string());
        lib_map.insert("silk-gui".to_string(), "https://github.com/Velvet-Lang/silk-gui.git".to_string());
        lib_map.insert("crux-lib".to_string(), "https://github.com/Velvet-Lang/crux-lib.git".to_string());
        lib_map.insert("nestdb-lib".to_string(), "https://github.com/Velvet-Lang/nestdb-lib.git".to_string());
        lib_map.insert("aegis-lib".to_string(), "https://github.com/Velvet-Lang/aegis-lib.git".to_string());

        DepResolver { available_deps, lib_map, lib_versions }
    }

    pub fn resolve(&self, code: &str, file_path: &str) -> Result<Vec<String>, String> {
        let mut dependencies = Vec::new();
        let lines = code.lines().enumerate();
        let project_dir = Path::new(file_path).parent().unwrap_or(Path::new("."));
        let lib_dir = project_dir.join("weave-library");

        fs::create_dir_all(&lib_dir).ok();

        for (line_num, line) in lines {
            let trimmed = line.trim();
            if trimmed.starts_with('<') && trimmed.ends_with('>') {
                let dep = trimmed.trim_start_matches('<').trim_end_matches('>').trim().to_string();
                if dep.is_empty() {
                    return Err(format!("{}:{}: Empty dep", "error".red().bold(), line_num + 1));
                }
                if self.available_deps.contains(&dep) {
                    dependencies.push(dep.clone());
                } else if let Some(url) = self.lib_map.get(&dep) {
                    let ver = self.lib_versions.get(&dep).cloned().unwrap_or_default();
                    let clone_path = lib_dir.join(&dep);
                    if !clone_path.exists() {
                        self.clone_with_version(&dep, &clone_path, &ver).ok();
                    }
                    dependencies.push(format!("lib:{}", dep));
                } else if dep.starts_with("local:") {
                    let src = Path::new(&dep[6..]);
                    fs::copy(src, lib_dir.join(src.file_name().unwrap())).ok();
                    dependencies.push(dep.clone());
                } else if dep.ends_with(".tar.gz") {
                    Command::new("curl").args(&["-o", "tmp.tar.gz", &dep]).status().ok();
                    Command::new("tar").args(&["-xzf", "tmp.tar.gz", "-C", lib_dir.to_str().unwrap()]).status().ok();
                    dependencies.push(dep.clone());
                } else {
                    return Err(format!("{} Unknown dep '{}'", "error".red().bold(), dep));
                }
            }
        }
        Ok(dependencies)
    }

    pub fn resolve_file(&self, file_path: &str) -> Result<Vec<String>, String> {
        let code = fs::read_to_string(file_path)
            .map_err(|e| format!("{}: Failed to read {}: {}", "error".red().bold(), file_path, e))?;
        self.resolve(&code, file_path)
    }

    fn clone_with_version(&self, dep: &str, path: &Path, ver: &str) -> Result<()> {
        let url = self.lib_map.get(dep).unwrap();
        Command::new("git").args(&["clone", url, path.to_str().unwrap()]).status()?;
        if !ver.is_empty() {
            Command::new("git").current_dir(path).args(&["checkout", ver]).status()?;
        }
        Ok(())
    }

    pub fn update_lib(&self, lib_dir: &Path) -> Result<()> {
        for entry in fs::read_dir(lib_dir)? {
            let path = entry?.path();
            if path.is_dir() {
                let repo = Repository::open(&path)?;
                let stash = repo.stash_save(&Signature::now("weave", "update")?)?;
                Command::new("git").current_dir(&path).args(&["pull"]).status()?;
                if let Some(id) = stash {
                    repo.stash_pop(id, None)?;
                }
                println!("{} Updated {}", "success".green(), path.display());
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_valid_deps() {
        let resolver = DepResolver::new();
        let code = "<std> <math>\n~x=5;";
        let result = resolver.resolve(code, "test.vel");
        assert_eq!(result.unwrap(), vec!["std".to_string(), "math".to_string()]);
    }

    #[test]
    fn test_resolve_unknown_dep() {
        let resolver = DepResolver::new();
        let code = "<std> <unknown>";
        let result = resolver.resolve(code, "test.vel");
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Unknown dep 'unknown'"));
    }
}
