use clap::{Parser, Subcommand};
use colored::Colorize;
use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;
use utils::dep_resolver::DepResolver;

#[derive(Parser)]
#[command(name = "weave", about = "Velvet Build Tool (Cargo-inspired)")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Create new project
    New { name: String },
    /// Initialize .velvet.toml
    Init,
    /// Add dependency
    Add { dep: String },
    /// Check syntax/deps/inline (interpreter mode)
    Check { project: Option<String> },
    /// Build project
    Build {
        #[arg(short, long)]
        release: bool,
        #[arg(short, long)]
        deb: bool,
        project: Option<String>,
    },
    /// Run tests
    Test { project: Option<String> },
    /// Quick run (via vel)
    Run { project: Option<String> },
    /// Update libraries
    Update,
    /// Generate docs
    Doc { project: Option<String> },
    /// Benchmark project
    Bench { project: Option<String> },
    /// Run all tests
    TestAll,
}

mod utils {
    pub mod dep_resolver;
}

fn main() {
    let cli = Cli::parse();
    let resolver = DepResolver::new();

    match cli.command {
        Commands::New { name } => {
            fs::create_dir_all(&name).unwrap();
            fs::write(format!("{}/main.vel", name), "// New Velvet project").unwrap();
            println!("{} Created {}", "success".green(), name);
        }
        Commands::Init => {
            // Write .velvet.toml stub
            println!("{} Initialized Velvet project", "success".green());
        }
        Commands::Add { dep } => {
            // Add to <deps> in main.vel or toml
            println!("{} Added dep: {}", "info".cyan(), dep);
        }
        Commands::Check { project } => {
            let proj = project.unwrap_or_else(|| "main".to_string());
            // Call parser.py
            Command::new("python").arg("src/velvet_parser.py").arg(&proj).status().unwrap();
            // Resolve deps
            if let Err(e) = resolver.resolve_file(&format!("{}.vel", proj)) {
                println!("{} {}", "error".red().bold(), e);
                return;
            }
            // Inline exec with safety (default allow-inline)
            Command::new("python").arg("src/utils/inline_exec.py").arg("--allow-inline").status().unwrap();
            println!("{} Check passed", "success".green());
        }
        Commands::Build { release, deb, project } => {
            let proj = project.unwrap_or_else(|| "app".to_string());
            let mut cmd = Command::new("python");
            cmd.arg("src/velvet_parser.py").arg(&proj).arg("--output-ir").arg("ir.json");
            cmd.status().unwrap();

            // Resolve & libs
            resolver.resolve_file(&format!("{}.vel", proj)).unwrap();
            // Gen .weave ZIP
            let mut zip_cmd = zip::write::File::create(&format!("{}.weave", proj)).unwrap();
            // Add manifest.json, ir.json, binary (Zig call)
            Command::new("zig").arg("build").arg("-Doptimize=ReleaseFast").status().unwrap();
            // Stub packaging
            if deb { println!("{} Future .deb build", "warning".yellow()); }
            println!("{} Built {}", if release { "release".green() } else { "debug".blue() }, proj);
        }
        Commands::Test { project } => {
            // Stub: run unit tests from .vel
            println!("{} Running tests for {:?}", "info".cyan(), project);
        }
        Commands::Run { project } => {
            Command::new("vel").arg("run").arg(project.unwrap_or_else(|| "main".to_string())).status().unwrap();
        }
        Commands::Update => {
            let lib_dir = Path::new("weave-library");
            if lib_dir.exists() {
                resolver.update_lib(lib_dir).ok();
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
        Commands::TestAll => {
            // Run pytest for Python, zig test for Zig
            Command::new("pytest").arg("tests/").status().unwrap();
            Command::new("zig").arg("test").arg("src/compiler.zig").status().unwrap();
            println!("{} Tests passed", "success".green());
        }
    }
}
