# Model Selection

## The basic problem

The model ID you think is correct is often not the exact string the provider expects. OpenRouter is unforgiving about this. The error is a 400 with a "not a valid model ID" message. Always verify the exact ID against the provider before deploying.

## Keeping IDs in sync

If your system prompt describes which model is running, derive that description from your tier configuration at runtime -- do not hardcode it separately. A stale model name in the system prompt means your agent has an identity crisis every time it describes itself.

## Tier strategy

Run two tiers minimum:

- Fast tier: small, cheap, instruction-tuned model for routine responses
- Think tier: larger reasoning-capable model for complex tasks

Route by command or by task type. The cost difference between tiers is significant. Do not use the think tier for everything.

## What to look for in a fast tier model

Instruction following is the primary criterion, not raw benchmark performance. A model that scores well on MMLU but ignores your formatting directives is worse than a smaller model that does what it is told.

Current reliable options as of April 2026:
- mistralai/mistral-small-3.2-24b-instruct:2506 -- strong instruction following, open-weight, cheap
- meta-llama/llama-3.3-70b-instruct -- larger, more capable, still reasonable cost

Avoid reasoning models on the fast tier unless you explicitly want chain-of-thought output. They resist formatting instructions and burn tokens on internal reasoning you do not need for simple tasks.

## Avoiding problematic models

Not all open-weight models are equivalent in what they will and will not say. Some models have built-in content suppression mechanisms that silence output on specific topics or groups of people. This is an architectural decision by the model provider, not a configuration option.

Before deploying any model in production, test it on the topics relevant to your use case. If a model will not discuss certain subjects, that is a permanent constraint on what your agent can do -- not something you can prompt your way around.

## Monitoring drift

The open-weight benchmark landscape moves fast. A model that is the right choice today may be superseded in six weeks. Build monitoring into your operation:

- Track benchmark releases from major providers
- Set a review cadence -- quarterly at minimum
- Consider running an agent that monitors OpenRouter releases and flags significant movements

Do not rely on your initial model selection indefinitely. The landscape rewards operators who stay current.
