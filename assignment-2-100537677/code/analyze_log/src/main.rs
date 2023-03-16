use std::env;
use std::process;

use analyze_log::{JobRunner, Job};

// cargo run -- ../../logs/batchmanager.log tenant2
fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("Please provide a file name and tenant name");
        process::exit(1);
    }
    let job = Job::build(args[2].clone(), args[1].clone());
    println!("{}", job);
    // 使用将trait引入作用域的方式调用特征方法
    match job.run() {
        Ok(count) => println!("Successful rows: {}", count),
        Err(e) => {
            println!("Application error: {}", e);
            process::exit(1);
        }
    }
}

