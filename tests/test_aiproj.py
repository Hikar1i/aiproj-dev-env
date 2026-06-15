import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "aiproj.py"


def run_cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class AiprojTests(unittest.TestCase):
    def test_help_works(self):
        result = run_cli(["--help"], ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Initialize a personal AI-assisted", result.stdout)

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
            result = run_cli(["init", "--dry-run"], repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN CREATE", result.stdout)
            self.assertFalse((repo / ".ai-local").exists())
            self.assertFalse((repo / "README.md").exists())

    def test_init_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
            first = run_cli(["init"], repo)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = run_cli(["init"], repo)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertTrue((repo / ".ai-local" / "config.json").exists())
            self.assertTrue((repo / "README.md").exists())
            self.assertTrue((repo / "docs" / "01-project-background.md").exists())
            self.assertTrue((repo / "AGENTS.override.md").exists())
            exclude = (repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
            self.assertIn("/.ai-local/", exclude)

    def test_skip_testing_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
            result = run_cli(["init", "--profile", "demo", "--skip-doc", "testing-strategy"], repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((repo / "docs" / "06-testing-strategy.md").exists())
            config = (repo / ".ai-local" / "config.json").read_text(encoding="utf-8")
            self.assertIn("testing-strategy", config)


if __name__ == "__main__":
    unittest.main()
