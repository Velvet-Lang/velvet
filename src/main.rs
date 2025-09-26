use clap::{Parser, Subcommand};
use colored::Colorize;
use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;
use git2::Repository;
use utils::dep_resolver::DepResolver;

#[derive(Parser)]
#[command(name = "weave", about = "Velvet Build Tool")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    New { name: String },
    Init,
    Add { dep: String },
    Check { project: Option<String> },
    Build {
        #[arg(short, long)]
        release: bool,
        #[arg(short, long)]
        deb: bool,
        project: Option<String>,
    },
    Test { project: Option<String> },
    Run { project: Option<String> },
    Update,  // New: Update libs
    Doc { project: Option<String> },  // Gen docs
    Bench { project: Option<String> },  // Benchmark
}

fn main() {
    let cli = Cli::parse();
    let resolver = DepResolver::new();

    match cli.command {
        // ... existing commands
        Commands::Update => {
            let lib_dir = Path::new("weave-library");
            if lib_dir.exists() {
                for entry in fs::read_dir(lib_dir).unwrap() {
                    let path = entry.unwrap().path();
                    if path.is_dir() {
                        if let Ok(repo) = Repository::open(&path) {
                            repo.find_remote("origin").and_then(|r| r.fetch(&["main"], None, None)).ok();
                            // Simplified pull
                            Command::new("git").current_dir(&path).args(&["pull"]).status().ok();
                            println!("{} Updated {}", "success".green(), path.display());
                        }
                    }
                }
            } else {
                println!("{} No weave-library found", "warning".yellow());
            }
        }
        Commands::Doc { project } => {
            let proj = project.unwrap_or_else(|| "main".to_string());
            // Stub: Gen docs from comments/decorators
            println!("{} Generating docs for {}", "info".cyan(), proj);
            Command::new("python").arg("src/velvet_parser.py").arg("--gen-doc").arg(&proj).status().unwrap();
        }
        Commands::Bench { project } => {
            let proj = project.unwrap_or_else(|| "main".to_string());
            // Stub: Build release + time exec
            println!("{} Benchmarking {}", "info".cyan(), proj);
            Command::new("./weave").arg("build").arg("--release").arg(&proj).status().unwrap();
            // Time run
        }
    }
}
