import sys
import time
import tracemalloc

def get_collatz_steps(n):
    steps = 0
    val = n
    while val > 1:
        if val % 2 == 0:
            val = val // 2
        else:
            val = 3 * val + 1
        steps += 1
    return steps

def run_benchmark(limit):
    tracemalloc.start()
    start_time = time.perf_counter()
    
    max_steps = 0
    max_num = 0
    
    for i in range(1, limit + 1):
        steps = get_collatz_steps(i)
        if steps > max_steps:
            max_steps = steps
            max_num = i
            
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_ms = (end_time - start_time) * 1000.0
    peak_mb = peak / (1024 * 1024)
    
    print(f"Max steps: {max_steps} for number: {max_num}")
    print(f"Time: {elapsed_ms:.2f} ms")
    print(f"Memory: {peak_mb:.4f} MB")

if __name__ == "__main__":
    limit = 2000000
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    run_benchmark(limit)
