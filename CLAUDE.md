# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TTS Evaluation - A Python project for evaluating text-to-speech systems.

## Development Environment

- **Python Version**: 3.12 (specified in `.python-version`)
- **Package Manager**: uv (based on `pyproject.toml` structure)
- **Dependencies**: Managed in `pyproject.toml`

## Common Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies (if using uv)
uv pip install -e .
```

### Running the Project
```bash
# Run main script
python main.py
```

### Testing
No test framework is currently configured. When tests are added, they will likely use pytest.

## Project Structure

- `main.py` - Entry point for the application
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version specification for pyenv/similar tools

## Architecture Notes

This is an early-stage project. As the codebase grows, expect to add:
- TTS model evaluation logic
- Audio processing utilities
- Metrics calculation modules
- Data loading and preprocessing
