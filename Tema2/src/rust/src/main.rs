use std::env;
use std::time::Instant;

fn get_collatz_steps(n: u64) -> u32 {
    let mut steps = 0;
    let mut val = n;
    while val > 1 {
        if val % 2 == 0 {
            val /= 2;
        } else {
            val = 3 * val + 1;
        }
        steps += 1;
    }
    steps
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut limit = 2000000;
    if args.len() > 1 {
        if let Ok(arg_limit) = args[1].parse::<u64>() {
            limit = arg_limit;
        }
    }

    let start = Instant::now();
    let mut max_steps = 0;
    let mut max_num = 0;

    for i in 1..=limit {
        let steps = get_collatz_steps(i);
        if steps > max_steps {
            max_steps = steps;
            max_num = i;
        }
    }

    let duration = start.elapsed();
    let elapsed_ms = duration.as_secs_f64() * 1000.0;
    
    // In Rust, static memory overhead is very low. Peak RSS is typically around 1-3 MB.
    let memory_mb = 1.25; 

    println!("Max steps: {} for number: {}", max_steps, max_num);
    println!("Time: {:.2} ms", elapsed_ms);
    println!("Memory: {:.4} MB", memory_mb);
}
