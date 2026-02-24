import argparse
import os
import re
from datetime import datetime
from pathlib import Path


BASE_PATH_ENV_VAR = "CHRONOECHO_BASE_PATH"
COMMAND_NAME = "chronoecho-history"


def parse_target_date(date_str=None, now=None):
    current = now or datetime.now()
    if date_str is None:
        return current.strftime("%m-%d"), current.strftime("%Y-%m-%d")

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str[5:], date_str

    if re.fullmatch(r"\d{2}-\d{2}", date_str):
        datetime.strptime(f"2000-{date_str}", "%Y-%m-%d")
        return date_str, f"{current.year}-{date_str}"

    raise ValueError("invalid date format")


def is_valid_date(date_str):
    try:
        parse_target_date(date_str)
        return True
    except ValueError:
        return False


def discover_base_path(start_path=None, max_depth=6):
    search_root = (
        Path(start_path or Path(__file__).resolve().parent).expanduser().resolve()
    )
    best_path = None
    best_score = (-1, 0)

    for current_root, dirnames, _ in os.walk(search_root):
        current_path = Path(current_root)
        depth = len(current_path.relative_to(search_root).parts)
        if depth >= max_depth:
            dirnames[:] = []
            continue

        dirnames[:] = [name for name in dirnames if not name.startswith(".")]
        year_dirs = [
            name
            for name in dirnames
            if len(name) == 4
            and name.isdigit()
            and (current_path / name / "Daily").is_dir()
        ]

        if year_dirs:
            score = (len(year_dirs), -depth)
            if score > best_score:
                best_score = score
                best_path = current_path

    return best_path


def resolve_base_path(base_path=None, env=None, start_path=None):
    if base_path:
        return Path(base_path).expanduser()

    env_map = os.environ if env is None else env
    env_base_path = env_map.get(BASE_PATH_ENV_VAR)
    if env_base_path:
        return Path(env_base_path).expanduser()

    discovered_path = discover_base_path(start_path=start_path)
    if discovered_path is not None:
        return discovered_path

    return Path(start_path or Path(__file__).resolve().parent).expanduser().resolve()


def scan_history_records(target_date=None, base_path=None, now=None, print_func=print):
    resolved_base_path = resolve_base_path(base_path=base_path)
    month_day, target_display = parse_target_date(target_date, now=now)

    try:
        years = [year for year in os.listdir(resolved_base_path) if year.isdigit()]
        years.sort()
    except Exception as exc:
        print_func(f"无法访问目录 {resolved_base_path}: {exc}")
        return False

    found = False
    for year in years:
        daily_path = os.path.join(resolved_base_path, year, "Daily")
        if not os.path.exists(daily_path):
            continue

        month_path = os.path.join(daily_path, month_day[:2])
        if not os.path.exists(month_path):
            continue

        year_date = f"{year}-{month_day}"
        date_md = os.path.join(month_path, f"{year_date}.md")
        date_dir = os.path.join(month_path, year_date)

        if os.path.exists(date_md) or os.path.exists(date_dir):
            print_func(f"在 {year} 年找到匹配记录:")
            if os.path.exists(date_md):
                print_func(f"- 文件: \033[36m{date_md}\033[0m")
            if os.path.exists(date_dir):
                print_func(f"- 文件夹: \033[34m{date_dir}\033[0m")
            found = True

    if not found:
        print_func(f"未找到日期 {target_display} 对应的任何历史记录")

    return found


def main(argv=None):
    parser = argparse.ArgumentParser(prog=COMMAND_NAME, description="查找历史记录")
    parser.add_argument(
        "date",
        nargs="?",
        help="指定要查找的日期 (YYYY-MM-DD 或 MM-DD 格式)",
        default=None,
    )
    parser.add_argument(
        "--base-path",
        dest="base_path",
        default=None,
        help=f"指定历史记录基础路径 (默认读取环境变量 {BASE_PATH_ENV_VAR} 或自动发现)",
    )
    args = parser.parse_args(argv)

    if args.date and not is_valid_date(args.date):
        print("错误: 请使用正确的日期格式 YYYY-MM-DD 或 MM-DD")
        return 1

    scan_history_records(args.date, base_path=args.base_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
