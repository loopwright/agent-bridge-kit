#!/usr/bin/env python3
"""
bridge_reference.py -- Reference bridge implementation for loopwright agent-bridge-kit.

This is a starting point, not a framework. Read it, understand it, adapt it.
Strip what you do not need. Add what you do.

Implements:
- Two model tiers (fast / think) via OpenRouter
- Formatting enforcement via per-message injection
- Truncation detection via finish_reason check
- Token logging to SQLite
- Daily spend warning
- systemd watchdog integration
"""

import sqlite3
import subprocess
import time
from datetime import datetime, date

import yaml
import structlog
from openai import OpenAI

logger = structlog.get_logger()

# --- Configuration ---
DB_PATH = "/home/user/agent/archive.db"
SECRETS_PATH = "/home/user/agent/secrets.enc.yaml"

# Model tiers. Verify IDs against OpenRouter before deploying.
TIERS = {
    "fast": {
        "model": "mistralai/mistral-small-3.2-24b-instruct:2506",
        "max_tokens": 4096,
        "label": "Mistral Small 3.2",
    },
    "think": {
        "model": "openai/gpt-oss-120b",
        "max_tokens": 8000,
        "label": "GPT-OSS 120B",
    },
}

# Cost per million tokens (input, output). Keep current with provider pricing.
MODEL_RATES = {
    "mistralai/mistral-small-3.2-24b-instruct:2506": {"input": 0.10, "output": 0.30},
    "openai/gpt-oss-120b": {"input": 0.039, "output": 0.19},
}

FORMATTING_REMINDER = "[FORMATTING RULE: Plain text only. No markdown. No asterisks, no bold, no headers, no bullet points.]"

SYSTEM_PROMPT = """FORMATTING RULE: Plain text only. No markdown. No asterisks, no bold, no headers, no bullet points. Never use * or ** for any reason. Code blocks only when producing actual code.

You are [AGENT NAME]. [AGENT DESCRIPTION].

[REMAINDER OF SYSTEM PROMPT]"""

# --- Secrets ---
def load_secrets():
    result = subprocess.run(["sops", "--decrypt", SECRETS_PATH], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"SOPS decrypt failed: {result.stderr}")
    raw = yaml.safe_load(result.stdout)
    return yaml.safe_load(raw["data"])

# --- Database ---
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        model TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS token_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        model TEXT NOT NULL,
        input_tokens INTEGER NOT NULL,
        output_tokens INTEGER NOT NULL,
        cost_usd REAL NOT NULL
    )""")
    conn.commit()
    return conn

def log_tokens(conn, model, input_tokens, output_tokens):
    rates = MODEL_RATES.get(model, {"input": 0.0, "output": 0.0})
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
    conn.execute(
        "INSERT INTO token_log (timestamp, model, input_tokens, output_tokens, cost_usd) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), model, input_tokens, output_tokens, cost)
    )
    conn.commit()

def today_spend(conn):
    row = conn.execute(
        "SELECT SUM(cost_usd) FROM token_log WHERE timestamp LIKE ?",
        (date.today().isoformat() + "%",)
    ).fetchone()
    return row[0] or 0.0

# --- LLM call ---
def call_llm(client, tier_config, messages, conn):
    """
    Call the LLM with formatting enforcement and truncation detection.

    Injects formatting reminder into the last user message before dispatch.
    Checks finish_reason and appends truncation notice if max_tokens was hit.
    """
    # Inject formatting reminder into last user message
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] = messages[-1]["content"] + "\n\n" + FORMATTING_REMINDER

    response = client.chat.completions.create(
        model=tier_config["model"],
        messages=messages,
        max_tokens=tier_config["max_tokens"],
    )

    msg = response.choices[0]
    content = msg.message.content or ""

    # Truncation detection
    if msg.finish_reason == "length":
        content = content + "\n[TRUNCATED -- max_tokens hit. Ask me to continue.]"

    # Token logging
    try:
        log_tokens(conn, tier_config["model"], response.usage.prompt_tokens, response.usage.completion_tokens)
    except Exception:
        pass

    return content

# --- Spend warning ---
DAILY_LIMIT = 8.00

def check_spend_warning(conn):
    spend = today_spend(conn)
    if spend >= DAILY_LIMIT:
        return f"WARNING: Daily spend at ${spend:.4f} -- ${DAILY_LIMIT} threshold reached."
    return None

# --- Watchdog ---
def notify_watchdog():
    """Signal systemd watchdog. Call in your main loop."""
    try:
        import sdnotify
        sdnotify.SystemdNotifier().notify("WATCHDOG=1")
    except Exception:
        pass

# --- Main loop stub ---
def main():
    secrets = load_secrets()
    client = OpenAI(
        api_key=secrets["openrouter_api_key"],
        base_url="https://openrouter.ai/api/v1",
    )
    conn = init_db()
    current_tier = "fast"

    # Replace this with your actual message source -- Matrix, Telegram, HTTP, etc.
    while True:
        notify_watchdog()
        time.sleep(1)

if __name__ == "__main__":
    main()
