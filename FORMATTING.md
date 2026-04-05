# Formatting Enforcement

## The problem

You write a system prompt that says, clearly, in the first line: plain text only, no markdown, no asterisks. The agent responds with bullet points and bold headers.

You try a different model. Same result. You move the instruction to the bottom of the prompt. Same result.

This is not a model capability problem. It is a prompt positioning problem.

Models weight recent context heavily. By the time the model generates its response, the system prompt is ancient history. Your formatting directive is a note left on a desk three days ago.

## The fix

Inject the formatting constraint immediately before every response -- appended to the user message, not buried in the system prompt.

In your message preparation code, before building the messages payload:

    if history and history[-1]["role"] == "user":
        history[-1]["content"] = history[-1]["content"] + "\n\n[FORMATTING RULE: Plain text only. No markdown. No asterisks, no bold, no headers, no bullet points.]"

When the formatting rule is the last thing the model sees before it generates, it sticks. When it is in the system prompt and nowhere else, it is advisory.

## Keep the system prompt rule too

Leave the formatting directive in your system prompt as well. The system prompt version sets the expectation. The per-message injection enforces it. Both together are more reliable than either alone.

## Model variation

Some models are more resistant than others. Reasoning-class models in particular tend to override formatting instructions because they are optimised to produce structured output. If you are running a reasoning model on a tier where plain text matters, the per-message injection is not optional -- it is the only thing that works.
