import argparse
import os
import subprocess
from pathlib import Path

from chronoecho_history import BASE_PATH_ENV_VAR


DEFAULT_BAT_NAME = "chronoecho_history.bat"


def normalize_windows_cmd_path(path_value):
    path_text = str(Path(path_value).expanduser())

    # Convert WSL path (/mnt/c/...) to Windows path (C:\...)
    if (
        path_text.startswith("/mnt/")
        and len(path_text) > 6
        and path_text[5].isalpha()
        and path_text[6] == "/"
    ):
        drive = path_text[5].upper()
        rest = path_text[7:].replace("/", "\\")
        return f"{drive}:\\{rest}" if rest else f"{drive}:\\"

    # Convert MSYS-style path (/c/...) to Windows path (C:\...)
    if (
        path_text.startswith("/")
        and len(path_text) > 3
        and path_text[1].isalpha()
        and path_text[2] == "/"
    ):
        drive = path_text[1].upper()
        rest = path_text[3:].replace("/", "\\")
        return f"{drive}:\\{rest}" if rest else f"{drive}:\\"

    return path_text


def find_default_startup_dir(appdata=None):
    raw_appdata = appdata if appdata is not None else os.environ.get("APPDATA")
    if not raw_appdata:
        raise RuntimeError("无法确定 APPDATA，请使用 --startup-dir 指定目录")

    appdata_path = Path(raw_appdata).expanduser()
    return appdata_path / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def resolve_startup_dir(startup_dir=None, appdata=None):
    if startup_dir:
        return Path(startup_dir).expanduser()
    return find_default_startup_dir(appdata=appdata)


def build_run_command(
    script_path,
    python_executable=None,
    date_arg=None,
):
    script = normalize_windows_cmd_path(script_path)
    python_path = normalize_windows_cmd_path(python_executable or "python")
    cmd_parts = [python_path, script]

    if date_arg:
        cmd_parts.append(date_arg)
    return subprocess.list2cmdline(cmd_parts)


def build_bat_content(
    script_path,
    python_executable=None,
    base_path=None,
    date_arg=None,
    pause=True,
):
    command = build_run_command(
        script_path=script_path,
        python_executable=python_executable,
        date_arg=date_arg,
    )

    lines = ["@echo off", "setlocal"]
    if base_path:
        lines.append(f'set "{BASE_PATH_ENV_VAR}={base_path}"')
    lines.append(command)
    if pause:
        lines.append("pause")
    lines.append("endlocal")
    return "\r\n".join(lines) + "\r\n"


def write_startup_bat(
    startup_dir, content, bat_name=DEFAULT_BAT_NAME, overwrite=False
):
    startup_path = Path(startup_dir).expanduser()
    startup_path.mkdir(parents=True, exist_ok=True)
    bat_path = startup_path / bat_name

    if bat_path.exists() and not overwrite:
        raise FileExistsError(
            f"{bat_path} 已存在，使用 --overwrite 可覆盖"
        )

    bat_path.write_text(content, encoding="utf-8", newline="")
    return bat_path


def install_startup_bat(
    script_path,
    startup_dir=None,
    python_executable=None,
    bat_name=DEFAULT_BAT_NAME,
    base_path=None,
    date_arg=None,
    pause=True,
    overwrite=False,
):
    script = Path(script_path).expanduser().resolve()
    startup = resolve_startup_dir(startup_dir=startup_dir)
    content = build_bat_content(
        script_path=script,
        python_executable=python_executable,
        base_path=base_path,
        date_arg=date_arg,
        pause=pause,
    )
    bat_path = write_startup_bat(
        startup_dir=startup,
        content=content,
        bat_name=bat_name,
        overwrite=overwrite,
    )
    return bat_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="写入 Windows 开机启动脚本")
    parser.add_argument(
        "--script-path",
        default=Path(__file__).with_name("chronoecho_history.py"),
        help="要执行的 Python 脚本路径，默认是当前目录下 chronoecho_history.py",
    )
    parser.add_argument(
        "--startup-dir",
        default=None,
        help="Startup 目录，默认根据 APPDATA 自动推断",
    )
    parser.add_argument(
        "--python",
        dest="python_executable",
        default=None,
        help="用于执行脚本的 Python 可执行文件路径（默认 python）",
    )
    parser.add_argument(
        "--bat-name",
        default=DEFAULT_BAT_NAME,
        help=f"生成的 bat 文件名，默认 {DEFAULT_BAT_NAME}",
    )
    parser.add_argument(
        "--base-path",
        default=None,
        help=f"写入环境变量 {BASE_PATH_ENV_VAR}，固定历史记录基础路径",
    )
    parser.add_argument(
        "--date",
        dest="date_arg",
        default=None,
        help="可选，启动时固定传给脚本的日期参数 (YYYY-MM-DD 或 MM-DD)",
    )
    parser.add_argument(
        "--no-pause",
        dest="pause",
        action="store_false",
        default=True,
        help="禁用 pause；脚本执行后窗口会自动关闭",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="若 bat 已存在则覆盖",
    )
    args = parser.parse_args(argv)

    script = Path(args.script_path).expanduser()
    if not script.exists():
        print(f"错误: 脚本不存在: {script}")
        return 1

    try:
        bat_path = install_startup_bat(
            script_path=script,
            startup_dir=args.startup_dir,
            python_executable=args.python_executable,
            bat_name=args.bat_name,
            base_path=args.base_path,
            date_arg=args.date_arg,
            pause=args.pause,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"写入失败: {exc}")
        return 1

    print(f"已写入启动脚本: {bat_path}")
    if args.pause:
        print("窗口将停留并等待手动关闭（pause 已启用）。")
    else:
        print("提示: 已禁用 pause，窗口执行后会自动关闭。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
