# GDShell

GDShell is a Python-powered hybrid shell + Textual dashboard designed for gamers and developers with a required Rust backend for parsing and external command execution.

## Features

- Custom interactive shell (`gdsh`) built with `prompt_toolkit`
- Built-in shell commands: `cd`, `ls`, `cat`, `clear`, `exit`
- GDSH gamer/dev commands:
  - `games`
  - `addgame`
  - `playtime`
  - `pingtest <host>`
  - `mods <game>`
  - `idea`
  - `sysinfo`
  - `dashboard`
- Command history, colored prompt, autocomplete, syntax highlighting
- Async command execution (internal and external commands)
- Rust backend (`rust_backend/`) used by Python shell for:
  - command-line parsing
  - external process execution
- Textual dashboard with panel layout and keyboard actions
- JSON-backed game library management
- Ping latency sampling with color-coded bars
- System snapshot metrics (CPU/RAM/temperatures)
- Mod config file preview (`.ini`, `.cfg`, `.json`, `.xml`)
- Random game idea generator

## Project Structure

```text
gdshell/
├── gdsh/
│   ├── shell.py
│   ├── rust_bridge.py
│   ├── commands.py
│   ├── parser.py
│   └── utils.py
├── tui/
│   ├── dashboard.py
│   ├── panels/
│   │   ├── games.py
│   │   ├── system.py
│   │   ├── ping.py
│   │   └── mods.py
│   └── widgets/
├── core/
│   ├── gamelib.py
│   ├── ping.py
│   ├── sysinfo.py
│   └── idea.py
├── rust_backend/
│   ├── Cargo.toml
│   └── src/main.rs
├── data/
│   └── games.json
├── main.py
└── README.md
```

## Requirements

- Python 3.10+
- Rust toolchain (`cargo`) required

Install Python dependencies:

```bash
pip install prompt_toolkit textual psutil pygments
```

Build Rust backend:

```bash
cargo build --release --manifest-path rust_backend/Cargo.toml
```

## Usage

Start shell:

```bash
python main.py
```

Open dashboard from inside shell:

```text
gdsh$ dashboard
```

## Notes

- GDShell will attempt to build `rust_backend` automatically if `gdsh-rs` is missing.
- Unknown commands are executed via the Rust backend.
- Game data is persisted in `data/games.json`.
- Dashboard keys: `q` quit, `r` refresh, `i` generate new game idea.
