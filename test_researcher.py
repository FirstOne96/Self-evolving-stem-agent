import unittest
from types import SimpleNamespace
from unittest.mock import patch

from stem.researcher import run_researcher


def _fake_response(content: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ]
    )


class TestResearcher(unittest.TestCase):
    def test_run_researcher_parses_valid_json(self):
        raw_json = (
            '{'
            '"domain": "QA / Bug Finding", '
            '"summary": "A concise summary", '
            '"tools": [], '
            '"architectures": [], '
            '"prompt_patterns": [], '
            '"failure_modes": [], '
            '"recommended_approach": {'
            '"architecture": "critic loop", '
            '"key_tools": [], '
            '"system_prompt_focus": "reliability", '
            '"evaluation_strategy": "benchmark"'
            '}'
            '}'
        )

        with patch(
            "stem.researcher.client.chat.completions.create",
            return_value=_fake_response(raw_json),
        ) as mock_create:
            result = run_researcher("QA / Bug Finding", verbose=False)

        self.assertEqual(result["domain"], "QA / Bug Finding")
        self.assertIn("recommended_approach", result)

        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["temperature"], 0.3)
        self.assertEqual(kwargs["max_tokens"], 2000)
        self.assertEqual(kwargs["messages"][1]["role"], "user")
        self.assertIn("Domain: QA / Bug Finding", kwargs["messages"][1]["content"])

    def test_run_researcher_parses_markdown_fenced_json(self):
        fenced = (
            "```json\n"
            "{\"domain\": \"Code Generation\", \"summary\": \"x\", \"tools\": [], "
            "\"architectures\": [], \"prompt_patterns\": [], \"failure_modes\": [], "
            "\"recommended_approach\": {\"architecture\": \"single agent\", "
            "\"key_tools\": [], \"system_prompt_focus\": \"clarity\", "
            "\"evaluation_strategy\": \"tests\"}}\n"
            "```"
        )

        with patch(
            "stem.researcher.client.chat.completions.create",
            return_value=_fake_response(fenced),
        ):
            result = run_researcher("Code Generation", verbose=False)

        self.assertEqual(result["domain"], "Code Generation")

    def test_run_researcher_raises_value_error_on_invalid_json(self):
        with patch(
            "stem.researcher.client.chat.completions.create",
            return_value=_fake_response("not json"),
        ):
            with self.assertRaises(ValueError):
                run_researcher("Anything", verbose=False)


if __name__ == "__main__":
    unittest.main()
