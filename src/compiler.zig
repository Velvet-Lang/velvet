const std = @import("std");

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    const args = std.process.argsAlloc(allocator) catch unreachable;
    defer std.process.argsFree(allocator, args);

    if (args.len > 1 and std.mem.eql(u8, args[1], "--ir-input")) {
        const ir_path = args[2];
        const ir_file = std.fs.cwd().openFile(ir_path, .{}) catch unreachable;
        defer ir_file.close();
        var buf: [1024]u8 = undefined;
        const ir_content = ir_file.readAll(&buf) catch unreachable;
        // Parse JSON (stub: assume simple)
        std.debug.print("IR loaded: {s}\n", .{ir_content});
        // Gen binary: e.g., emit C, compile
        const c_code = "int main() { return 0; }";  // From AST
        std.fs.cwd().writeFile("out.c", c_code) catch unreachable;
        const gcc = Command.new("gcc").args(&[_][]const u8{ "out.c", "-o", "out" }).spawn() catch unreachable;
        _ = gcc.wait() catch unreachable;
    }
    std.debug.print("Zig codegen complete.\n", .{});
}

const Command = struct {
    // Stub Command impl
};
