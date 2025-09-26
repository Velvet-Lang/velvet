use std::collections::HashSet;
use std::fs;
use std::path::Path;
use colored::Colorize;

pub struct DepResolver {
    available_deps: HashSet<String>,
}

impl DepResolver {
    pub fn new() -> Self {
        let mut available_deps = HashSet::new();
        // Hypothetical standard library dependencies
        available_deps.insert("std".to_string());
        available_deps.insert("math".to_string());
        available_deps.insert("io".to_string());
        // Add more as needed
        DepResolver { available_deps }
    }

    pub fn resolve(&self, code: &str, file_path: &str) -> Result<Vec<String>, String> {
        let mut dependencies = Vec::new();
        let lines = code.lines().enumerate();

        for (line_num, line) in lines {
            let trimmed = line.trim();
            if trimmed.starts_with('<') && trimmed.ends_with('>') {
                let dep = trimmed.trim_start_matches('<').trim_end_matches('>').trim();
                if dep.is_empty() {
                    return Err(format!(
                        "{}:{}: {}: Empty dependency declaration",
                        file_path,
                        line_num + 1,
                        "error".red().bold()
                    ));
                }
                if !self.available_deps.contains(dep) {
                    return Err(format!(
                        "{}:{}: {}: Unknown dependency '{}'. Available: {:?}",
                        file_path,
                        line_num + 1,
                        "error".red().bold(),
                        dep,
                        self.available_deps
                    ));
                }
                dependencies.push(dep.to_string());
            }
        }

        Ok(dependencies)
    }

    pub fn resolve_file(&self, file_path: &str) -> Result<Vec<String>, String> {
        let code = fs::read_to_string(file_path)
            .map_err(|e| format!("{}: Failed to read {}: {}", "error".red().bold(), file_path, e))?;
        self.resolve(&code, file_path)
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
        assert_eq!(result.unwrap(), vec!["std", "math"]);
    }

    #[test]
    fn test_resolve_unknown_dep() {
        let resolver = DepResolver::new();
        let code = "<std> <unknown>";
        let result = resolver.resolve(code, "test.vel");
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Unknown dependency 'unknown'"));
    }
}
