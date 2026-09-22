# HAL — Python Dependency Hell, Finally Fixed

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered pip wrapper that detects Python dependency conflicts and attempts to fix them automatically.

## The Problem

Python's dependency management has been a well-documented pain point for over a decade. When two packages require conflicting versions of the same dependency, `pip` throws a confusing error — and the developer is left to manually figure out what's wrong and how to fix it.

**HAL automates that process:**
- Detects conflicts (built on top of `pip check`)
- Uses AI (Groq API) to explain the error in plain language
- Attempts an automatic fix — e.g., upgrading a conflicting package to a compatible version

## Installation

```bash
pip install hal-ai
```

## Usage

```bash
hal init              # set up a new project (venv + pyproject.toml)
hal add <package>       # install a package; HAL will try to resolve conflicts
hal doctor               # check for conflicts
hal doctor --fix         # attempt to auto-fix conflicts
```

## Example

```
$ hal doctor --fix
HAL Doctor --fix mode (SMART)
googletrans 3.1.0a0 has requirement httpx==0.13.3, but you have httpx 0.27.2.

HAL SMART FIX: googletrans is outdated, upgrading it...
HAL is resolving: googletrans==4.0.0rc1...
SUCCESS: googletrans==4.0.0rc1 installed!
```

## AI Setup

To enable AI-powered explanations and fixes, you'll need a free Groq API key (get one at console.groq.com):

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_key_here"

# Mac/Linux
export GROQ_API_KEY="your_key_here"
```

## Status

Early-stage working prototype. Core features (install, conflict detection, AI-assisted resolution) are tested and functional. Feedback and contributions welcome.

## License

MIT