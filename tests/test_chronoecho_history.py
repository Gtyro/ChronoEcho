import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import chronoecho_history


class HistoryFinderTests(unittest.TestCase):
    def test_is_valid_date_supports_year_month_day_and_month_day(self):
        self.assertTrue(chronoecho_history.is_valid_date("2026-02-24"))
        self.assertTrue(chronoecho_history.is_valid_date("02-24"))
        self.assertTrue(chronoecho_history.is_valid_date("02-29"))

    def test_is_valid_date_rejects_invalid_inputs(self):
        self.assertFalse(chronoecho_history.is_valid_date("2026/02/24"))
        self.assertFalse(chronoecho_history.is_valid_date("13-24"))
        self.assertFalse(chronoecho_history.is_valid_date("2026-02-30"))

    def test_parse_target_date_for_month_day_uses_current_year_display(self):
        month_day, target_display = chronoecho_history.parse_target_date(
            "02-24", now=datetime(2026, 2, 1)
        )
        self.assertEqual(month_day, "02-24")
        self.assertEqual(target_display, "2026-02-24")

    def test_scan_history_records_supports_month_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "journal_root"
            month_2023 = base / "2023" / "Daily" / "02"
            month_2024 = base / "2024" / "Daily" / "02"
            month_2023.mkdir(parents=True)
            month_2024.mkdir(parents=True)

            (month_2023 / "2023-02-24.md").write_text("", encoding="utf-8")
            (month_2024 / "2024-02-24").mkdir()

            outputs = []
            found = chronoecho_history.scan_history_records(
                "02-24",
                base_path=base,
                now=datetime(2026, 2, 24),
                print_func=outputs.append,
            )

            self.assertTrue(found)
            output_text = "\n".join(outputs)
            self.assertIn("在 2023 年找到匹配记录:", output_text)
            self.assertIn("在 2024 年找到匹配记录:", output_text)
            self.assertIn("2023-02-24.md", output_text)
            self.assertIn("2024-02-24", output_text)

    def test_resolve_base_path_precedence_explicit_env_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            explicit = Path(tmp) / "explicit_base"
            env_path = Path(tmp) / "env_base"
            search_root = Path(tmp) / "search_root"
            discovered_path = search_root / "discovered_base"
            explicit.mkdir()
            env_path.mkdir()
            (discovered_path / "2024" / "Daily").mkdir(parents=True)

            resolved_explicit = chronoecho_history.resolve_base_path(
                base_path=str(explicit),
                env={chronoecho_history.BASE_PATH_ENV_VAR: str(env_path)},
                start_path=search_root,
            )
            resolved_env = chronoecho_history.resolve_base_path(
                env={chronoecho_history.BASE_PATH_ENV_VAR: str(env_path)},
                start_path=search_root,
            )
            resolved_discovered = chronoecho_history.resolve_base_path(
                env={},
                start_path=search_root,
            )

            self.assertEqual(resolved_explicit, explicit)
            self.assertEqual(resolved_env, env_path)
            self.assertEqual(resolved_discovered, discovered_path)

    def test_discover_base_path_finds_year_daily_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            candidate = home / "any" / "path"
            competitor = home / "other"

            (candidate / "2023" / "Daily").mkdir(parents=True)
            (candidate / "2024" / "Daily").mkdir(parents=True)
            (competitor / "2022" / "Daily").mkdir(parents=True)

            discovered = chronoecho_history.discover_base_path(
                start_path=home, max_depth=6
            )
            self.assertEqual(discovered, candidate)


if __name__ == "__main__":
    unittest.main()
