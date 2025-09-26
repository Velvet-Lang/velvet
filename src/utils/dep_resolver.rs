use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::Path;
use colored::Colorize;
use std::process::Command;

pub struct DepResolver {
    available_deps: std::collections::HashSet<String>,
    lib_map: HashMap<String, String>,  // name -> url
}

impl DepResolver {
    pub fn new() -> Self {
        let mut available_deps = std::collections::HashSet::new();
        available_deps.insert("std".to_string());
        available_deps.insert("math".to_string());
        available_deps.insert("io".to_string());

        let mut lib_map = HashMap::new();
        // Fetch library.weave
        let temp_dir = env::temp_dir();
        let lib_file = temp_dir.join("library.weave");
        let fetch_url = "https://raw.githubusercontent.com/Velvet-Lang/velvet/main/weave/library.weave";
        if cfg!(target_os = "windows") {
            // Windows: Use powershell Invoke-WebRequest
            Command::new("powershell")
                .args(&["Invoke-WebRequest", "-Uri", fetch_url, "-OutFile", lib_file.to_str().unwrap()])
                .status().ok();
        } else {
            // Linux: curl
            Command::new("curl").args(&["-o", lib_file.to_str().unwrap(), fetch_url]).status().ok();
        }
        if lib_file.exists() {
            let content = fs::read_to_string(&lib_file).unwrap_or_default();
            for line in content.lines() {
                let parts: Vec<&str> = line.split(" > ").collect();
                if parts.len() == 2 {
                    lib_map.insert(parts[0].trim().to_string(), parts[1].trim().to_string());
                }
            }
        }
        // Fallback to example
        lib_map.insert("crich-cli".to_string(), "https://github.com/Velvet-Lang/crich-cli.git".to_string());
        lib_map.insert("silk-gui".to_string(), "https://github.com/Velvet-Lang/silk-gui.git".to_string());
        lib_map.insert("crux-lib".to_string(), "https://github.com/Velvet-Lang/crux-lib.git".to_string());
        lib_map.insert("nestdb-lib".to_string(), "https://github.com/Velvet-Lang/nestdb-lib.git".to_string());
        lib_map.insert("aegis-lib".to_string(), "https://github.com/Velvet-Lang/aegis-lib.git".to_string());

        DepResolver { available_deps, lib_map }
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
                    let clone_path = lib_dir.join(&dep);
                    if !clone_path.exists() {
                        Command::new("git").args(&["clone", url, clone_path.to_str().unwrap()]).status().ok();
                        if !clone_path.exists() {
                            return Err(format!("{} Failed to clone {}", "error".red().bold(), dep));
                        }
                    }
                    dependencies.push(format!("lib:{}", dep));
                } else {
                    return Err(format!("{} Unknown dep '{}'", "error".red().bold(), dep));
                }
            }
        }
        Ok(dependencies)
    }

    // ... existing resolve_file, tests
}
