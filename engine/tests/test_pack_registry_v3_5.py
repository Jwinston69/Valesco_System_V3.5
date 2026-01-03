import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import engine.modules.pack_registry_v3_5 as pack_registry


class TestPackRegistryV35(unittest.TestCase):
    def setUp(self) -> None:
        self._reset_registry()

    def tearDown(self) -> None:
        self._reset_registry()

    def _reset_registry(self) -> None:
        pack_registry._REGISTRY = None
        pack_registry._REGISTRY_ROOT = None
        pack_registry._LOGGED = False

    def _write_yaml(self, root_dir: str, rel_path: str, content: str) -> None:
        path = Path(root_dir) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_required_packs(self, root_dir: str) -> None:
        self._write_yaml(root_dir, "library/packs/valesco_pack.yaml", "pack: true\n")
        self._write_yaml(root_dir, "library/core/valesco_materials.yaml", "materials: []\n")
        self._write_yaml(root_dir, "library/core/valesco_subcontractors.yaml", "subcontractors: []\n")
        self._write_yaml(root_dir, "library/core/valesco_tasks.yaml", "groups: {}\n")

    def test_nominal_load(self) -> None:
        with TemporaryDirectory() as temp_dir:
            self._write_required_packs(temp_dir)

            pack_registry.initialize_registry(root_dir=temp_dir, log=False)

            self.assertTrue(pack_registry.is_initialized())
            self.assertEqual(pack_registry.get_pack()["pack"], True)
            self.assertEqual(
                pack_registry.get_registry_root(),
                Path(temp_dir).resolve(),
            )
            self.assertEqual(pack_registry.get_pack(), pack_registry.get_pack())

    def test_missing_required_authority_pack_fails(self) -> None:
        with TemporaryDirectory() as temp_dir:
            self._write_yaml(temp_dir, "library/packs/valesco_pack.yaml", "pack: true\n")
            self._write_yaml(temp_dir, "library/core/valesco_materials.yaml", "materials: []\n")
            self._write_yaml(temp_dir, "library/core/valesco_tasks.yaml", "groups: {}\n")

            with self.assertRaisesRegex(RuntimeError, "library/core/valesco_subcontractors.yaml"):
                pack_registry.initialize_registry(root_dir=temp_dir, log=False)

            self.assertFalse(pack_registry.is_initialized())

    def test_single_load_is_idempotent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            self._write_required_packs(temp_dir)

            pack_registry.initialize_registry(root_dir=temp_dir, log=False)

            with patch("engine.modules.pack_registry_v3_5._load_yaml") as mock_load:
                pack_registry.initialize_registry(root_dir=temp_dir, log=False)

            mock_load.assert_not_called()

    def test_duplicate_pack_entry_fails(self) -> None:
        with TemporaryDirectory() as temp_dir:
            self._write_required_packs(temp_dir)

            duplicate_pack_order = [
                ("pack", "library/packs/valesco_pack.yaml", "pricing-authority"),
                ("pack_duplicate", "library/packs/valesco_pack.yaml", "pricing-authority"),
                ("materials", "library/core/valesco_materials.yaml", "pricing-authority"),
                ("subcontractors", "library/core/valesco_subcontractors.yaml", "pricing-authority"),
                ("tasks", "library/core/valesco_tasks.yaml", "productivity-only"),
            ]

            with patch.object(pack_registry, "_PACK_ORDER", duplicate_pack_order):
                with self.assertRaisesRegex(RuntimeError, "duplicate entries"):
                    pack_registry.initialize_registry(root_dir=temp_dir, log=False)


if __name__ == "__main__":
    unittest.main()
