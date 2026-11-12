import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "configure_sync.py"
WORKFLOW = Path(".github") / "workflows" / "agentz-sync.yml"
MANIFEST = '{"name": "example", "version": "1.0.0", "description": "Example.", "author": {"name": "Ex"}}'


class ConfigureSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".git").mkdir()
        (self.root / ".claude-plugin").mkdir()
        (self.root / ".claude-plugin" / "plugin.json").write_text(MANIFEST, encoding="utf-8")
        (self.root / "README.md").write_text("# Example\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def run_setup(self, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source", str(self.root), "--category", "development",
             "--owner-handle", "@example", "--owner-email", "owner@example.test", *extra],
            capture_output=True, text=True, check=False,
        )

    def test_preview_writes_nothing_and_apply_writes_only_the_workflow(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview only", result.stdout)
        self.assertFalse((self.root / WORKFLOW).exists())

        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        self.assertEqual(set(after) - set(before), {Path(".github"), Path(".github/workflows"), WORKFLOW})
        workflow = (self.root / WORKFLOW).read_text(encoding="utf-8")
        self.assertNotRegex(workflow, r"__[A-Z_]+__")
        self.assertIn('- ".claude-plugin/plugin.json"', workflow)
        self.assertIn('--plugin-path "."', workflow)
        self.assertIn('OWNER_EMAIL: "owner@example.test"', workflow)

    def test_plugin_in_subfolder_scopes_the_trigger(self):
        sub = self.root / "plugin"
        sub.mkdir()
        (self.root / ".claude-plugin" / "plugin.json").rename(sub / "plugin.json")
        (self.root / "README.md").rename(sub / "README.md")
        result = self.run_setup("--apply", "--plugin-path", "./plugin/")
        self.assertEqual(result.returncode, 0, result.stderr)
        workflow = (self.root / WORKFLOW).read_text(encoding="utf-8")
        self.assertIn('- "plugin/plugin.json"', workflow)
        self.assertIn('--plugin-path "plugin"', workflow)

    def test_requires_an_existing_plugin(self):
        (self.root / ".claude-plugin" / "plugin.json").unlink()
        result = self.run_setup("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already use the plugin layout", result.stderr)
        self.assertFalse((self.root / WORKFLOW).exists())

    def test_rejects_unsafe_inputs(self):
        cases = {
            "traversal": ("--plugin-path", "../outside"),
            "injection": ("--marketplace-repository", "owner/repo\n  injected: true"),
            "handle": ("--owner-handle", "nobody"),
        }
        for label, extra in cases.items():
            with self.subTest(label):
                result = self.run_setup("--apply", *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / WORKFLOW).exists())

    def test_existing_different_workflow_needs_force(self):
        (self.root / WORKFLOW).parent.mkdir(parents=True)
        (self.root / WORKFLOW).write_text("custom", encoding="utf-8")
        result = self.run_setup("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / WORKFLOW).read_text(encoding="utf-8"), "custom")
        result = self.run_setup("--apply", "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual((self.root / WORKFLOW).read_text(encoding="utf-8"), "custom")


if __name__ == "__main__":
    unittest.main()
