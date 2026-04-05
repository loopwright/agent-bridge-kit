# agent-bridge-kit

## What this is

A reference implementation of the bridge architecture for running AI agents in production on a bare Linux VPS. Model tier configuration, formatting enforcement, truncation detection, token logging, and a systemd service file.

Companion to [agent-spec-kit](https://github.com/loopwright/agent-spec-kit). The spec tells you what the agent is. This kit is how you actually run it without it failing silently in three different directions at once.

## The problem

Most agent tutorials end at "call the API and print the response." Production is different. In production:

- Models ignore formatting directives unless you enforce them at the right point in the message chain
- Models hit token limits and stop mid-response with no warning unless you check finish_reason
- Model IDs drift out of sync with what you think you are running
- Processes crash and restart into port conflicts
- Token costs accumulate invisibly until they do not

None of these are capability problems. They are infrastructure problems. This kit addresses them.

## What is in the kit

    agent-bridge-kit/
    README.md                   (this file)
    bridge_reference.py         (annotated reference bridge implementation)
    agent.service               (systemd service file with watchdog)
    FORMATTING.md               (the formatting directive problem and fix)
    MODEL_SELECTION.md          (how to pick models, verify IDs, handle drift)
    CHECKLIST.md                (pre-deployment checklist)

## How to use it

1. Read FORMATTING.md and MODEL_SELECTION.md first -- these are the failure modes most people hit
2. Use bridge_reference.py as a starting point, not a framework
3. Run through CHECKLIST.md before going live
4. File agent.service under systemd and adapt paths to your setup

## Platform compatibility

The bridge uses the OpenAI-compatible API format. Works with any provider that supports it:

- OpenRouter (recommended -- single API, 200+ models)
- Anthropic direct
- Any open-weight model via Ollama or vLLM

## Who this is for

Independent operators running agents on their own infrastructure. If you are on managed hosting with a GUI, this is probably more than you need. If you are on a VPS with a terminal and a budget, this is built for you.

## About loopwright

We build automation tools for independent operators. Everything we sell, we use ourselves. This kit is the architecture we run in production.

Questions: loopwrightdev@proton.me
