# Pre-Deployment Checklist

## Model configuration
- [ ] Model IDs verified against provider -- exact strings, not approximations
- [ ] Fast tier and think tier both tested with a real message
- [ ] Model names in system prompt match actual TIERS config
- [ ] Reasoning mode disabled on fast tier if using a hybrid model

## Formatting enforcement
- [ ] Formatting directive present in system prompt
- [ ] Formatting directive injected into every user message before dispatch
- [ ] Tested with a prompt that would naturally produce markdown -- confirmed plain text output

## Truncation detection
- [ ] finish_reason checked on every response
- [ ] Truncation notice appended when finish_reason is "length"
- [ ] max_tokens set appropriately for each tier -- not too low, not unbounded

## Token management
- [ ] Token logging active -- input and output tracked per call
- [ ] Daily spend limit configured with warning threshold
- [ ] Cost rates accurate for current models

## Process management
- [ ] systemd service file in place with Restart=on-failure
- [ ] WatchdogSec configured -- detects hung processes, not just crashes
- [ ] Port conflict procedure documented -- stop service, kill orphans, confirm port clear, start clean
- [ ] Service tested: stop, start, restart all behave correctly

## Secrets
- [ ] No credentials in source code or environment variables
- [ ] Secrets encrypted at rest -- SOPS+age or equivalent
- [ ] Secrets decrypted at runtime only, not stored as permanent env vars
- [ ] Secrets file excluded from version control

## Comms
- [ ] Inbound message routing tested end to end
- [ ] Outbound message delivery confirmed
- [ ] Error states surface to operator -- agent does not fail silently
