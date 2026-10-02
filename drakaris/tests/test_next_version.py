from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from next_version import (  # noqa: E402
    find_current_version,
    increment_version,
    parse_requested_version,
    resolve_next,
)


class IncrementTests(unittest.TestCase):
    def test_v1_0_to_v1_1(self) -> None:
        self.assertEqual(increment_version("v1.0"), "v1.1")

    def test_v1_1_to_v1_2(self) -> None:
        self.assertEqual(increment_version("v1.1"), "v1.2")

    def test_v3_26_to_v3_27(self) -> None:
        self.assertEqual(increment_version("v3.26"), "v3.27")

    def test_one_component_becomes_minor(self) -> None:
        self.assertEqual(increment_version("v1"), "v1.1")

    def test_three_component_increments_patch(self) -> None:
        self.assertEqual(increment_version("v1.0.0"), "v1.0.1")


class RequestedVersionTests(unittest.TestCase):
    def test_pin_drakaris_v1_5(self) -> None:
        self.assertEqual(parse_requested_version("drakaris v1.5"), "v1.5")

    def test_pin_versao_2_0(self) -> None:
        self.assertEqual(parse_requested_version("drakaris versão 2.0"), "v2.0")

    def test_pin_versao_sem_acento(self) -> None:
        self.assertEqual(parse_requested_version("drakaris versao 2.0"), "v2.0")

    def test_example_list_does_not_pin(self) -> None:
        msg = (
            "quando rodar o drakaris sempre incrementar a versão da imagem gerada, "
            "exemplo: v1.0, v1.1, v1.2, a não ser que eu diga a versão que deve ser gerada"
        )
        self.assertIsNone(parse_requested_version(msg))

    def test_bare_drakaris_does_not_pin(self) -> None:
        self.assertIsNone(parse_requested_version("drakaris"))


class CurrentVersionTests(unittest.TestCase):
    def test_empty_repo_has_no_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(find_current_version(Path(tmp)))

    def test_reads_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v1.0\n", encoding="utf-8")
            self.assertEqual(find_current_version(Path(tmp)), "v1.0")

    def test_yaml_image_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "deploy.yaml").write_text(
                "image: kiwel/horus:v3.26\n", encoding="utf-8"
            )
            self.assertEqual(find_current_version(Path(tmp)), "v3.26")

    def test_yaml_takes_max(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.yaml").write_text("image: kiwel/app:v1.0\n", encoding="utf-8")
            Path(tmp, "b.yml").write_text("image: kiwel/app:v1.2\n", encoding="utf-8")
            self.assertEqual(find_current_version(Path(tmp)), "v1.2")

    def test_ignores_latest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "deploy.yaml").write_text(
                "image: kiwel/app:latest\nimage: kiwel/app:v1.0\n",
                encoding="utf-8",
            )
            self.assertEqual(find_current_version(Path(tmp)), "v1.0")

    def test_version_file_wins_over_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v2.0\n", encoding="utf-8")
            Path(tmp, "deploy.yaml").write_text(
                "image: kiwel/app:v1.9\n", encoding="utf-8"
            )
            self.assertEqual(find_current_version(Path(tmp)), "v2.0")

    def test_ignores_github_workflow_third_party(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gh = Path(tmp, ".github", "workflows")
            gh.mkdir(parents=True)
            gh.joinpath("test.yml").write_text(
                "image: mcr.microsoft.com/playwright:v1.62.1-jammy\n",
                encoding="utf-8",
            )
            Path(tmp, "deploy.yaml").write_text(
                "image: kiwel/vikunjax:v1.0\n", encoding="utf-8"
            )
            self.assertEqual(find_current_version(Path(tmp)), "v1.0")


class ResolveTests(unittest.TestCase):
    def test_no_history_is_v1_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(resolve_next(Path(tmp), "drakaris"), "v1.0")

    def test_increments_from_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v1.0\n", encoding="utf-8")
            self.assertEqual(resolve_next(Path(tmp), "drakaris"), "v1.1")

    def test_write_creates_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v1.0\n", encoding="utf-8")
            tag = resolve_next(Path(tmp), "drakaris", write=True)
            self.assertEqual(tag, "v1.1")
            self.assertEqual(Path(tmp, "VERSION").read_text(encoding="utf-8"), "v1.1\n")

    def test_pin_overrides_increment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v1.0\n", encoding="utf-8")
            self.assertEqual(resolve_next(Path(tmp), "drakaris v1.5"), "v1.5")


class CliTests(unittest.TestCase):
    def test_cli_prints_tag(self) -> None:
        script = ROOT / "next_version.py"
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "VERSION").write_text("v1.1\n", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--repo",
                    tmp,
                    "--message",
                    "drakaris",
                    "--write",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.stdout.strip(), "v1.2")
            self.assertEqual(Path(tmp, "VERSION").read_text(encoding="utf-8"), "v1.2\n")


if __name__ == "__main__":
    unittest.main()
