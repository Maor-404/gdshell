use std::env;
use std::io::{self, Write};
use std::process::{Command, ExitCode};

struct ParseResult {
    command: String,
    args: Vec<String>,
}

fn json_escape(input: &str) -> String {
    let mut escaped = String::with_capacity(input.len());
    for ch in input.chars() {
        match ch {
            '\\' => escaped.push_str("\\\\"),
            '"' => escaped.push_str("\\\""),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            c if c.is_control() => escaped.push_str(&format!("\\u{:04x}", c as u32)),
            c => escaped.push(c),
        }
    }
    escaped
}

fn to_json(parsed: &ParseResult) -> String {
    let args = parsed
        .args
        .iter()
        .map(|arg| format!("\"{}\"", json_escape(arg)))
        .collect::<Vec<String>>()
        .join(",");
    format!(
        "{{\"command\":\"{}\",\"args\":[{}]}}",
        json_escape(&parsed.command),
        args
    )
}

fn parse_line(line: &str) -> Result<ParseResult, String> {
    let mut tokens: Vec<String> = Vec::new();
    let mut current = String::new();
    let mut in_single = false;
    let mut in_double = false;
    let mut chars = line.chars().peekable();

    while let Some(ch) = chars.next() {
        match ch {
            '\\' if !in_single => {
                if let Some(next) = chars.next() {
                    current.push(next);
                } else {
                    return Err("parse error: dangling escape".to_string());
                }
            }
            '\'' if !in_double => in_single = !in_single,
            '"' if !in_single => in_double = !in_double,
            c if c.is_whitespace() && !in_single && !in_double => {
                if !current.is_empty() {
                    tokens.push(current.clone());
                    current.clear();
                }
            }
            c => current.push(c),
        }
    }

    if in_single || in_double {
        return Err("parse error: unclosed quote".to_string());
    }
    if !current.is_empty() {
        tokens.push(current);
    }

    if tokens.is_empty() {
        return Ok(ParseResult {
            command: String::new(),
            args: vec![],
        });
    }

    Ok(ParseResult {
        command: tokens[0].clone(),
        args: tokens[1..].to_vec(),
    })
}

fn run_external(command: &str, args: &[String]) -> i32 {
    let status = Command::new(command).args(args).status();
    match status {
        Ok(s) => s.code().unwrap_or(1),
        Err(err) => {
            let _ = writeln!(io::stderr(), "failed to run '{command}': {err}");
            1
        }
    }
}

fn print_help() {
    println!(
        "gdsh-rs usage:\n  gdsh-rs parse <line>\n  gdsh-rs exec <command> [args...]\n\nSubcommands:\n  parse   Parse shell line and print JSON\n  exec    Execute external command and stream output"
    );
}

fn main() -> ExitCode {
    let mut argv = env::args().skip(1);
    let Some(mode) = argv.next() else {
        print_help();
        return ExitCode::SUCCESS;
    };

    match mode.as_str() {
        "parse" => {
            let line = argv.collect::<Vec<String>>().join(" ");
            match parse_line(&line) {
                Ok(parsed) => {
                    println!("{}", to_json(&parsed));
                    ExitCode::SUCCESS
                }
                Err(err) => {
                    eprintln!("{err}");
                    ExitCode::from(1)
                }
            }
        }
        "exec" => {
            let Some(command) = argv.next() else {
                eprintln!("exec requires a command");
                return ExitCode::from(2);
            };
            let args = argv.collect::<Vec<String>>();
            ExitCode::from(run_external(&command, &args) as u8)
        }
        _ => {
            print_help();
            ExitCode::from(2)
        }
    }
}
