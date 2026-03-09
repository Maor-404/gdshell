# GDShell

GDShell is a Python-powered hybrid shell + Textual dashboard designed for gamers and developers.

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
├── data/
│   └── games.json
├── main.py
└── README.md
```

## Requirements

Python 3.10+

Install dependencies:

```bash
pip install prompt_toolkit textual psutil pygments
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

- Unknown commands fall back to direct executable invocation.
- Game data is persisted in `data/games.json`.
- Dashboard keys: `q` quit, `r` refresh, `i` generate new game idea.
