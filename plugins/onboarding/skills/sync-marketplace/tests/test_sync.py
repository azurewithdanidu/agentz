import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[5]
spec = importlib.util.spec_from_file_location("agentz_sync", Path(__file__).resolve().parents[1] / "scripts" / "sync.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
lib, gate = sync.load_lib(REPO)

SHA = "a" * 40


def args(**overrides):
    values = {"source_repository": "owner/source", "source_sha": SHA, "plugin_path": ".", "category": "development",
              "owner_handle": "@owner", "base_branch": "main"}
    return argparse.Namespace(**{**values, **overrides})


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.market = Path(self.temporary.name)
        (self.market / ".claude-plugin").mkdir()
        (self.market / ".github").mkdir()
        (self.market / "plugins" / "local").mkdir(parents=True)
        self.registry = {"name": "agentz", "owner": {"name": "o"}, "plugins": [
            {"name": "local", "source": "./plugins/local", "description": "d", "category": "development"}]}
        self.save_registry()
        (self.market / ".github" / "CODEOWNERS").write_text("* @admins\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def save_registry(self):
        (self.market / ".claude-plugin" / "marketplace.json").write_text(json.dumps(self.registry), encoding="utf-8")

    def load_registry(self):
        return json.loads((self.market / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    def manifest(self, name="demo", version="1.0.0"):
        raw = {"name": name, "version": version, "description": "Demo plugin.", "author": {"name": "Me"},
               "agents": ["./agents"], "keywords": ["x"]}
        return sync.normalise_manifest(raw, lib, "me@example.test")

    def test_new_plugin_copies_files_and_pins_the_source(self):
        result = sync.update_marketplace(self.market, lib, self.manifest(), "# Demo\n", args(plugin_path="./plugin/"))
        self.assertIsNone(result)
        entry = self.load_registry()["plugins"][-1]
        self.assertEqual(entry["source"], {"source": "github", "repo": "owner/source", "sha": SHA, "path": "plugin"})
        copy = json.loads((self.market / "plugins" / "demo" / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("agents", copy)
        self.assertEqual(copy["author"], {"name": "Me", "email": "me@example.test"})
        self.assertEqual((self.market / "plugins" / "demo" / "README.md").read_text(encoding="utf-8"), "# Demo\n")
        self.assertIn("/plugins/demo/ @owner", (self.market / ".github" / "CODEOWNERS").read_text(encoding="utf-8"))

    def test_update_needs_a_version_bump(self):
        sync.update_marketplace(self.market, lib, self.manifest(), "# Demo\n", args())
        reason = sync.update_marketplace(self.market, lib, self.manifest(), "# Changed\n", args(source_sha="b" * 40))
        self.assertIn("Bump the version", reason)
        self.assertEqual(self.load_registry()["plugins"][-1]["source"]["sha"], SHA)

        self.assertIsNone(sync.update_marketplace(self.market, lib, self.manifest(version="1.1.0"), "# Changed\n",
                                                  args(source_sha="b" * 40, category=None, owner_handle=None)))
        entry = self.load_registry()["plugins"][-1]
        self.assertEqual((entry["source"]["sha"], entry["category"]), ("b" * 40, "development"))
        self.assertEqual(len(self.load_registry()["plugins"]), 2)

    def test_refuses_name_collisions(self):
        with self.assertRaisesRegex(sync.SyncError, "lives in the marketplace"):
            sync.update_marketplace(self.market, lib, self.manifest(name="local"), "", args())
        sync.update_marketplace(self.market, lib, self.manifest(), "", args())
        with self.assertRaisesRegex(sync.SyncError, "already linked"):
            sync.update_marketplace(self.market, lib, self.manifest(version="2.0.0"), "", args(source_repository="x/y"))

    def test_secret_in_readme_stops_the_sync(self):
        with self.assertRaisesRegex(sync.SyncError, "GitHub token"):
            sync.scan_secrets({"README.md": "token ghp_" + "a" * 36}, gate.SECRET_PATTERNS)

    def test_publish_updates_an_open_pull_request(self):
        (self.market / ".git").mkdir()
        calls = []

        def fake_run(cmd, cwd, check=True):
            calls.append(cmd)
            out = "12\n" if cmd[:3] == ["gh", "pr", "list"] else ""
            return mock.Mock(returncode=0, stdout=out, stderr="")

        with mock.patch.object(sync, "run", fake_run):
            message = sync.publish(self.market, self.manifest(), args(), "body")
        self.assertEqual(message, "updated pull request #12")
        self.assertIn(["git", "push", "--force", "origin", "HEAD:refs/heads/agentz-sync/demo"], calls)
        self.assertTrue(any(c[:4] == ["gh", "pr", "edit", "12"] for c in calls))
        self.assertFalse(any(c[:3] == ["gh", "pr", "create"] for c in calls))


if __name__ == "__main__":
    unittest.main()
