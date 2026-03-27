# LangChain Practice: Memory + Routing Chat Assistant

This project is a CLI chat assistant built with LangChain and OpenRouter.

It supports:
- Intent-based routing (code explanation, summary request, or general chat)
- Session-based in-memory chat history
- Runtime session switching without restart

## Features

- Code topics -> detailed explanation chain
- Summary requests -> 2-line summary chain
- General questions -> normal memory-aware response chain
- Session memory commands:
  - `/session` to view current session id
  - `/switch <session_id>` to switch memory context

## Project Files

- `app.py`: Main application logic
- `.env`: Local secrets (not committed)
- `.env.example`: Example environment template
- `.gitignore`: Ignore rules for env, venv, caches, and local artifacts

## Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- OpenRouter API key

## Setup

1. Create and activate virtual environment (if not already active).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from template:

```bash
copy .env.example .env
```

(Use `cp .env.example .env` on macOS/Linux.)

4. Open `.env` and set your keys:

- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY` (can be same as OpenRouter key for compatibility)

## Run

```bash
python app.py
```

On start, app asks for a session id:
- Press Enter for `default-session`
- Or type custom id like `user1`

Then chat normally.

## In-Chat Commands

- `exit` or `quit`: Stop app
- `/session`: Show current session id
- `/switch <session_id>`: Switch to another chat memory

## Example

1. Start with session `user1`
2. Ask: `My name is Afzal`
3. Ask: `What is my name?`
4. Switch: `/switch user2`
5. Ask: `What is my name?`

`user2` will have separate memory from `user1`.

## Notes

- Memory is in-process only (`InMemoryChatMessageHistory`).
- If app restarts, memory resets.
- For persistent memory, use file/DB-backed chat history in future.
