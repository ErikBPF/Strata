# Serve extensions for decision clients

Two additions in this fork exist for lettered-readout decision clients (the pqnld shape:
ask a closed-set question and read the answer-slot distribution over option labels).

## `POST /tokenize`

Proves an option label is one token before it is scored, without running the model.

```sh
curl -s localhost:8080/tokenize -H 'content-type: application/json' -d '{"content":"в"}'
{"model": "...", "tokens": [5301], "count": 1}
```

Accepts llama.cpp's `content`, vLLM's `prompt`, or SGLang's `text`; `parse_special`
defaults to false.

## `STRATA_MAX_TOP_LOGPROBS`

OpenAI caps `top_logprobs` at 20, which bounds a lettered readout to ~20 options per
request. The environment variable raises that ceiling (default 20, clamped to 4096)
without changing the default OpenAI shape:

```sh
STRATA_MAX_TOP_LOGPROBS=160 strata serve --profile … --port 8080
```

Cost is one logprob slot per option in the answer line; a wide read widens the
engine's per-token work, so raise it per deployment, not globally.
