const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Define the main compiler executable
    const exe = b.addExecutable(.{
        .name = "weave",
        .root_source_file = b.path("src/compiler.zig"),
        .target = target,
        .optimize = optimize,
    });

    // Add dependencies (e.g., link with Rust output if needed)
    exe.addIncludePath(b.path("src"));
    // Example: Link with Rust static lib (assumes Cargo builds it)
    exe.addLibraryPath(b.path("."));
    exe.linkSystemLibrary("velvet_lang"); // Hypothetical Rust lib

    // Install the executable
    b.installArtifact(exe);

    // Custom step to invoke Python parser (velvet_parser.py)
    const run_python_parser = b.addSystemCommand(&[_][]const u8{
        "python",
        "src/velvet_parser.py",
    });
    run_python_parser.step.dependOn(&exe.step);

    // Custom build commands
    const build_cmd = b.addSystemCommand(&[_][]const u8{
        "zig",
        "build-exe",
        "src/compiler.zig",
        "--name",
        "weave",
    });
    b.step("build", "Build the Velvet compiler").dependOn(&build_cmd.step);

    // Release build
    const release_cmd = b.addSystemCommand(&[_][]const u8{
        "zig",
        "build-exe",
        "src/compiler.zig",
        "--name",
        "weave",
        "-O",
        "ReleaseFast",
    });
    b.step("release", "Build optimized Velvet compiler").dependOn(&release_cmd.step);

    // Package commands (deb, rpm, exe, appimage)
    const deb_cmd = b.addSystemCommand(&[_][]const u8{
        "zig",
        "build-exe",
        "src/compiler.zig",
        "--name",
        "weave.deb",
    });
    b.step("deb", "Build .deb package").dependOn(&deb_cmd.step);

    // Add more for rpm, exe, appimage as needed
}
