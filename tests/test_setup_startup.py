import tempfile
import unittest
from pathlib import Path

import setup_startup


class SetupStartupTests(unittest.TestCase):
    def test_find_default_startup_dir_returns_programs_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            appdata = Path(tmp) / "AppData" / "Roaming"
            appdata.mkdir(parents=True)
            found = setup_startup.find_default_startup_dir(appdata=appdata)
            expected = (
                appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            )
            self.assertEqual(found, expected)

    def test_build_bat_content_contains_command_and_env(self):
        content = setup_startup.build_bat_content(
            script_path=r"C:\work dir\ChronoEcho\chronoecho_history.py",
            python_executable=r"C:\Program Files\Python312\python.exe",
            base_path=r"D:\notes\journal",
            date_arg="02-24",
        )
        self.assertIn('@echo off\r\nsetlocal\r\n', content)
        self.assertIn('set "CHRONOECHO_BASE_PATH=D:\\notes\\journal"', content)
        self.assertIn('"C:\\Program Files\\Python312\\python.exe"', content)
        self.assertIn('"C:\\work dir\\ChronoEcho\\chronoecho_history.py" 02-24', content)
        self.assertIn("\r\npause\r\n", content)

    def test_build_bat_content_allows_disabling_pause(self):
        content = setup_startup.build_bat_content(
            script_path=r"C:\repo\chronoecho_history.py",
            pause=False,
        )
        self.assertNotIn("\r\npause\r\n", content)

    def test_build_run_command_uses_windows_python_invocation(self):
        command = setup_startup.build_run_command(
            script_path=r"C:\repo\chronoecho_history.py",
            python_executable="python",
            date_arg="02-24",
        )
        self.assertIn(r"python C:\repo\chronoecho_history.py 02-24", command)

    def test_build_run_command_converts_wsl_paths(self):
        command = setup_startup.build_run_command(
            script_path="/mnt/c/Users/demo/ChronoEcho/chronoecho_history.py",
            python_executable="/mnt/c/Program Files/Python312/python.exe",
        )
        self.assertIn('"C:\\Program Files\\Python312\\python.exe"', command)
        self.assertIn("C:\\Users\\demo\\ChronoEcho\\chronoecho_history.py", command)

    def test_normalize_windows_cmd_path_msys(self):
        self.assertEqual(
            setup_startup.normalize_windows_cmd_path("/d/notes/journal"),
            r"D:\notes\journal",
        )

    def test_write_startup_bat_respects_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            startup_dir = Path(tmp) / "Startup"
            content = "@echo off\r\n"

            bat = setup_startup.write_startup_bat(
                startup_dir=startup_dir,
                content=content,
                bat_name="chronoecho_history.bat",
                overwrite=False,
            )
            self.assertTrue(bat.exists())

            with self.assertRaises(FileExistsError):
                setup_startup.write_startup_bat(
                    startup_dir=startup_dir,
                    content=content,
                    bat_name="chronoecho_history.bat",
                    overwrite=False,
                )

            setup_startup.write_startup_bat(
                startup_dir=startup_dir,
                content="@echo off\r\nrem updated\r\n",
                bat_name="chronoecho_history.bat",
                overwrite=True,
            )
            self.assertIn("updated", bat.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
