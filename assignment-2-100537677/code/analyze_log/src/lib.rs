use std::fs;
use std::io::{prelude::*, BufReader};
use std::fmt;


pub trait JobRunner {
    fn run(&self) -> std::io::Result<i32>;
    // 默认实现
    fn talk(&self) {
        println!("I am a job runner");
    }
}

pub struct Job<T> {
    tenant_name: T,
    file_name: T,
}

impl<T>  Job<T> {
    pub fn build(tenant_name: T, file_name: T) -> Job<T> {
        Job {
            tenant_name,
            file_name,
        }
    }
}

// 针对特定类型(String)的实现
impl JobRunner for Job<String> {
    fn run(&self) -> std::io::Result<i32> {
        let file = fs::File::open(&self.file_name)?;
        let reader = BufReader::new(file);
        let mut success_count = 0;
        // 如果要使用一个特征的方法，那么需要将该特征引入当前的作用域中
        // lines() 定义在std::io::BufRead中
        for line in reader.lines() {
            let line = line?;
            if !line.contains(&self.tenant_name) || !line.contains("metrics"){
                continue;
            }
        let split = line.split(",");
        for part in split {
            if !part.contains("successful_rows") {
                continue;
            }
            let split: Vec<&str> = part.split(":").collect();
            let count = split[1].to_string().trim().parse::<i32>().unwrap();
            success_count += count;
        }
        }
        Ok(success_count)
    }

    fn talk(&self) {
        println!("I am a job runner for {}", self.tenant_name);
    }
}

impl fmt::Display for Job<String> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result{
        write!(f, "Custom output: tenant_name: {}, file_name: {}", &self.tenant_name, &self.file_name)
    }
}


// 特征约束trait bound
// 传入参数类型：&impl JobRunner，实现了JobRunner的类型都可以传入
// 是whoiam2的简写
pub fn whoiam(job: &impl JobRunner) {
    job.talk();
}

pub fn whoiam2<T: JobRunner>(job: &T) {
    job.talk();
}

// 多重约束
// 是whoiamout2的简写
pub fn whoiamout(job: &(impl JobRunner + fmt::Display)) {
    println!("{}", job);
}
pub fn whoiamout2<T: JobRunner + fmt::Display>(job: &T) {
    println!("{}", job);
}
// 和whoiamout2等价
pub fn whoiamout3<T>(job: &T) where T: JobRunner + fmt::Display {
    println!("{}", job);
}


// 特征对象
pub trait Draw {
    fn draw(&self);
}
#[derive(Clone)]
pub struct Button {
    pub width: u32,
    pub height: u32,
    pub label: String,
}

impl Draw for Button {
    fn draw(&self) {
        println!("Button");
    }
}
#[derive(Clone)]
pub struct SelectBox {
    pub width: u32,
    pub height: u32,
    pub options: Vec<String>,
}

impl Draw for SelectBox {
    fn draw(&self) {
        println!("SelectBox");
    }
}

pub struct Screen<'a> {
    // dyn 关键字只用在特征对象的类型声明
    // 可以通过 & 引用或者 Box<T> 智能指针的方式来创建特征对象
    pub components: Vec<Box<dyn Draw>>,
    pub components2: Vec<&'a dyn Draw>,
}

impl<'a> Screen<'a> {
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
        println!("------------------");
        for component in self.components2.iter() {
            component.draw();
        }
    }
}

//  cargo test -- --nocapture
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trait_bound() {
        let job = Job::build("tenant2".to_string(), "../../logs/batchmanager.log".to_string());
        whoiam(&job);
        whoiam2(&job);
    }

    #[test]
    fn multiple_trait_bound() {
        let job = Job::build("tenant2".to_string(), "../../logs/batchmanager.log".to_string());
        whoiamout(&job);
        whoiamout2(&job);
        whoiamout3(&job);
    }


    #[test]
    fn trait_object() {
        let b = Button {
            width: 100,
            height: 100,
            label: "OK".to_string(),
        };
        let s = SelectBox {
            width: 100,
            height: 100,
            options: vec![
                "Yes".to_string(),
                "No".to_string(),
                "Maybe".to_string(),
            ],
        };
        // 特征对象可以通过Box<T>或者&T来创建
        let screen = Screen {
            components: vec![
                Box::new(b.clone()),
                Box::new(s.clone()),
            ],
            components2: vec![
             &b, &s
            ]
        };
        screen.run();
    }
}