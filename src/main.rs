use std::env;
use std::process::Command;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("\x1b[31mError: weave build [options]\x1b[0m");
        return;
    }
    match args[1].as_str() {
        "build" => {
            // Call Python parser
            Command::new("python").arg("src/velvet_parser.py").status().unwrap();
            // Detailed errors like Cargo
            println!("\x1b[32mCompiling Velvet project...\x1b[0m");
            // ... integrate Zig
        }
        _ => println!("\x1b[31mUnknown command\x1b[0m"),
    }
}
