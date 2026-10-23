"""Synthetic multi-family/edition code generation conformance tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from bcast.rust_codegen import RuleCompilationError, main, transpile_rules

FIXTURE = (
    Path(__file__).resolve().parents[1] / "examples/synthetic/reviewed-rules.json"
)
SMOKE = Path(__file__).with_name("rust_codegen_smoke.rs")


class RuleCodegenTests(unittest.TestCase):
    def setUp(self):
        self.input = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_compiles_multiple_families_editions_deterministically(self):
        output = transpile_rules(self.input)
        self.assertEqual(output, transpile_rules(deepcopy(self.input)))
        self.assertIn('edition: "2024"', output)
        self.assertIn('edition: "2027"', output)
        self.assertIn('family: "synthetic-fire-code"', output)
        self.assertIn("Decision::Unsupported", output)
        self.assertNotIn("any licensed text", output)
        self.assertEqual(output.count("Edition { namespace:"), 3)

    def test_wrong_shape_and_unreviewed_rules_fail_closed(self):
        cases = []
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0].pop("review")
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0]["must"]["value"]["quantity"]["decimal"] = "NaN"
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0]["must"]["value"]["quantity"]["unit"] = ""
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"].append(deepcopy(bad["editions"][0]))
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0]["must"]["op"] = "inferred"
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0]["new_legal_text"] = "raw text"
        cases.append(bad)
        bad = deepcopy(self.input)
        bad["editions"][0]["rules"][0]["must"] = {"not": {"not": {"oops": True}}}
        cases.append(bad)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(RuleCompilationError):
                transpile_rules(case)

    def test_cli_creates_rust_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated.rs"
            self.assertEqual(main([str(FIXTURE), str(output)]), 0)
            self.assertTrue(output.read_text(encoding="utf-8").startswith("// AUTO-GENERATED"))

    @unittest.skipUnless(shutil.which("rustc"), "rustc is not installed")
    def test_generated_rust_compiles_and_evaluates_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "code_rules.rs"
            binary = Path(directory) / "test_rules"
            src.write_text(
                transpile_rules(self.input) + "\n" + SMOKE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            subprocess.run(
                ["rustc", "--edition=2021", "--test", str(src), "-o", str(binary)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run([str(binary)], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()