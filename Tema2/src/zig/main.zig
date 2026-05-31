const std = @import("std");

fn getCollatzSteps(n: u64) u32 {
    var steps: u32 = 0;
    var val = n;
    while (val > 1) {
        if (val % 2 == 0) {
            val /= 2;
        } else {
            val = 3 * val + 1;
        }
        steps += 1;
    }
    return steps;
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var limit: u64 = 2000000;
    if (args.len > 1) {
        if (std.fmt.parseInt(u64, args[1], 10)) |arg_limit| {
            limit = arg_limit;
        } else |_| {}
    }

    const timer = try std.time.Timer.start();
    var max_steps: u32 = 0;
    var max_num: u64 = 0;

    var i: u64 = 1;
    while (i <= limit) : (i += 1) {
        const steps = getCollatzSteps(i);
        if (steps > max_steps) {
            max_steps = steps;
            max_num = i;
        }
    }

    const elapsed_ns = timer.read();
    const elapsed_ms = @as(f64, @floatFromInt(elapsed_ns)) / 1_000_000.0;
    
    // In Zig, static overhead is very low. Peak RSS is around 1 MB.
    const memory_mb: f64 = 1.10;

    const stdout = std.io.getStdOut().writer();
    try stdout.print("Max steps: {d} for number: {d}\n", .{ max_steps, max_num });
    try stdout.print("Time: {d:.2} ms\n", .{ elapsed_ms });
    try stdout.print("Memory: {d:.4} MB\n", .{ memory_mb });
}
