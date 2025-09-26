const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "weave",
        .root_source_file = b.path("src/compiler.zig"),
        .target = target,
        .optimize = optimize,
    });

    exe.addIncludePath(b.path("src"));
    exe.linkSystemLibrary("velvet_lang");

    b.installArtifact(exe);

    // IR step: Consume JSON from stdin/file
    const ir_step = b.addSystemCommand(&[_][]const u8{
        "zig",
        "run",
        "src/compiler.zig",
        "--ir-input",
        "ir.json",  // From Rust parser
    });
    ir_step.step.dependOn(&exe.step);

    const build_cmd = b.addSystemCommand(&[_][]const u8{ "zig", "build-exe", "src/compiler.zig", "-O", "ReleaseFast" });
    b.step("release", "Optimized build").dependOn(&build_cmd.step);

    // Stub for packaging
    b.step("deb", "Future .deb packaging").dependOn(&build_cmd.step);
}
