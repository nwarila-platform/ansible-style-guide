# SPDX-FileCopyrightText: 2026 Smarter > Harder
# SPDX-License-Identifier: MIT
"""Exercise every role-discovery branch and display-path rule."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from rolecheck.__main__ import main
from rolecheck.discover import NAMESPACE_NAMES, PRUNE_NAMES, discover


class DiscoveryTests(unittest.TestCase):
    """Build isolated trees for namespace, pruning, and collision behavior."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_every_namespace_and_role_kind(self):
        expected = {
            "applications/app": ("app", "application"),
            "host_roles/host": ("host", "other"),
            "operating_systems/os": ("os", "other"),
            "roles/generic": ("generic", "other"),
            "utilities/tool": ("tool", "other"),
        }
        self.assertEqual(
            NAMESPACE_NAMES,
            {"applications", "host_roles", "operating_systems", "roles", "utilities"},
        )
        for role_path in expected:
            (self.root / role_path).mkdir(parents=True)
        actual = {
            role.role_path: (role.name, role.kind) for role in discover(self.root)
        }
        self.assertEqual(actual, expected)

    def test_empty_namespace_child_is_a_role(self):
        role = self.root / "applications/empty"
        role.mkdir(parents=True)
        self.assertEqual([item.path for item in discover(self.root)], [role])

    def test_non_namespace_child_is_not_a_role(self):
        (self.root / "ordinary/not_a_role/tasks").mkdir(parents=True)
        self.assertEqual(discover(self.root), [])

    def test_direct_namespace_and_tree_relative_paths(self):
        role = self.root / "applications/app"
        role.mkdir(parents=True)
        self.assertEqual(discover(role)[0].role_path, "app")
        self.assertEqual(discover(role.parent)[0].role_path, "app")
        self.assertEqual(discover(self.root)[0].role_path, "applications/app")

    def test_every_pruned_name_is_derived_from_the_constant(self):
        self.assertEqual(
            PRUNE_NAMES,
            {
                ".audit",
                ".cache",
                ".compose",
                ".frameworks",
                ".git",
                ".worktrees",
                "node_modules",
            },
        )
        intended = self.root / "applications/intended"
        intended.mkdir(parents=True)
        for prune_name in PRUNE_NAMES:
            with self.subTest(prune_name=prune_name):
                hidden = self.root / prune_name / "applications/hidden"
                hidden.mkdir(parents=True)
        self.assertEqual([item.role_path for item in discover(self.root)], ["applications/intended"])

    def test_symlinked_directory_is_not_followed(self):
        outside = self.root / "outside/applications/linked"
        outside.mkdir(parents=True)
        link = self.root / "link"
        try:
            link.symlink_to(self.root / "outside", target_is_directory=True)
        except OSError as error:
            self.skipTest(str(error))
        roles = discover(self.root)
        self.assertEqual([item.role_path for item in roles], ["outside/applications/linked"])
        self.assertTrue(all(not item.role_path.startswith("link/") for item in roles))

    def test_colliding_direct_role_paths_are_rejected(self):
        first = self.root / "first/applications/same"
        second = self.root / "second/roles/same"
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = main(["check", str(first), str(second)])
        self.assertEqual(status, 2)
        self.assertEqual(
            stderr.getvalue(),
            "error: role paths collide across PATH arguments\n",
        )
