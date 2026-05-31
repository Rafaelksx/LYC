const { performance } = require('perf_hooks');

function getCollatzSteps(n) {
    let steps = 0;
    let val = n;
    while (val > 1) {
        if (val % 2 === 0) {
            val = val / 2;
        } else {
            val = 3 * val + 1;
        }
        steps++;
    }
    return steps;
}

function runBenchmark(limit) {
    // Warm up and gc if possible (node flags)
    const startMemory = process.memoryUsage().heapUsed;
    const startTime = performance.now();
    
    let maxSteps = 0;
    let maxNum = 0;
    
    for (let i = 1; i <= limit; i++) {
        const steps = getCollatzSteps(i);
        if (steps > maxSteps) {
            maxSteps = steps;
            maxNum = i;
        }
    }
    
    const endTime = performance.now();
    const endMemory = process.memoryUsage().heapUsed;
    
    const elapsedMs = endTime - startTime;
    // Estimate memory overhead during execution
    const peakMemoryMb = (process.memoryUsage().rss) / (1024 * 1024);
    
    console.log(`Max steps: ${maxSteps} for number: ${maxNum}`);
    console.log(`Time: ${elapsedMs.toFixed(2)} ms`);
    console.log(`Memory: ${peakMemoryMb.toFixed(4)} MB`);
}

function main() {
    let limit = 2000000;
    if (process.argv.length > 2) {
        const argLimit = parseInt(process.argv[2], 10);
        if (!isNaN(argLimit)) {
            limit = argLimit;
        }
    }
    runBenchmark(limit);
}

main();
