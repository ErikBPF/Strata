# Serve extensions for decision clients

A lettered-readout decision client asks a closed-set question and reads the answer
slot's distribution over option labels. Two serve-layer additions cover that shape.

## `POST /tokenize`

Token ids for a string, without running the model. A client uses it to prove an
option label is one token before scoring it.

Accepts llama.cpp's `content`, vLLM's `prompt` or SGLang's `text`. `parse_special`
defaults to false. Response shape, with ids and count depending on the tokenizer:

```sh
curl -s localhost:8080/tokenize -H 'content-type: application/json' -d '{"content":"a"}'
# shape only, not a recorded run
{"model": "<model>", "tokens": [<id>, ...], "count": <n>}
```

## `STRATA_MAX_TOP_LOGPROBS`

OpenAI caps `top_logprobs` at 20, which bounds a readout to about 20 options per
request. The environment variable raises that ceiling (default 20, clamped to 4096)
and leaves the default shape alone:

```sh
STRATA_MAX_TOP_LOGPROBS=160 strata serve --profile … --port 8080
```

Each option costs one logprob slot at the answer line. A wide read widens the
engine's per-token work, so raise it per deployment.
