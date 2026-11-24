"""POST /tokenize and the configurable top_logprobs ceiling: python -m unittest serve.test_tokenize.

Both exist for decision clients (a lettered readout): the tokenizer proves an option label
is ONE token before it is scored, and the ceiling lets such a client see more than the
OpenAI default of 20 labels at the answer slot.
"""
from __future__ import annotations

import os
import unittest

from serve.server import ByteTokenizer, top_logprobs


class TokenizeCapability(unittest.TestCase):
    def test_tokenizer_maps_a_non_latin_label_to_ids(self):
        tok = ByteTokenizer()
        ids = tok.encode("\u0432")                 # Cyrillic ve
        self.assertEqual(len(ids), 2)              # one UTF-8 byte pair in the byte stand-in
        self.assertEqual(tok.decode(ids), "\u0432")

    def test_tokenize_handler_accepts_the_three_client_shapes(self):
        tok = ByteTokenizer()
        for body in ({"content": "ab"}, {"prompt": "ab"}, {"text": "ab"}):
            raw = body.get("content", body.get("prompt", body.get("text")))
            self.assertEqual(tok.encode(raw), [97, 98])


class TopLogprobsCeiling(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("STRATA_MAX_TOP_LOGPROBS", None)

    def test_default_ceiling_stays_at_openai_twenty(self):
        os.environ.pop("STRATA_MAX_TOP_LOGPROBS", None)
        self.assertEqual(top_logprobs({"logprobs": True, "top_logprobs": 60}), 20)
        self.assertEqual(top_logprobs({"logprobs": 60}), 20)

    def test_environment_raises_the_ceiling_for_decision_clients(self):
        os.environ["STRATA_MAX_TOP_LOGPROBS"] = "160"
        self.assertEqual(top_logprobs({"logprobs": True, "top_logprobs": 160}), 160)
        self.assertEqual(top_logprobs({"logprobs": 200}), 160)

    def test_bad_or_absurd_values_fall_back_safely(self):
        os.environ["STRATA_MAX_TOP_LOGPROBS"] = "not-a-number"
        self.assertEqual(top_logprobs({"logprobs": True, "top_logprobs": 60}), 20)
        os.environ["STRATA_MAX_TOP_LOGPROBS"] = "999999"
        self.assertEqual(top_logprobs({"logprobs": True, "top_logprobs": 999999}), 4096)


if __name__ == "__main__":
    unittest.main()
