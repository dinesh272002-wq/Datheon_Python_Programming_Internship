"""File Organizer.

Sorts the files in a folder (default: your Downloads folder) into category
subfolders such as Documents, Images, Videos, Archives and Code, based on the
file extension.

Usage:
    python organizer.py                      # organize ~/Downloads
    python organizer.py "C:/path/to/folder"  # organize a specific folder
    python organizer.py --dry-run            # only show what would happen
    python organizer.py --recursive          # also look inside subfolders
    python organizer.py --others             # move unknown types into /Others

Every action is written to the console and to organizer.log (next to this
script).
"""

import argparse
import logging
import os
import shutil
from pathlib import Path

# ---------- Configuration ----------

CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls",
                  ".xlsx", ".csv", ".ppt", ".pptx", ".md"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
                  ".tiff", ".ico"],
    "Videos":    [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Audio":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Archives":  [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code":      [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h",
                  ".json", ".xml", ".sh", ".ts", ".sql", ".ipynb"],
}

# extension -> category, e.g. {'.pdf': 'Documents', '.jpg': 'Images', ...}
EXTENSION_MAP = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}

OTHERS = "Others"

# Files that are still downloading or temporary: never touch these.
SKIP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "organizer.log"

log = logging.getLogger("organizer")


def setup_logging():
    log.setLevel(logging.INFO)
    log.handlers.clear()
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        log.addHandler(file_handler)
    except OSError as err:
        print(f"Warning: could not write log file ({err}). Logging to console only.")


# ---------- Helpers ----------

def unique_destination(dest_dir, filename):
    """Return a path in dest_dir that does not exist yet (adds _1, _2 ...)."""
    target = dest_dir / filename
    if not target.exists():
        return target
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        target = dest_dir / f"{stem}_{counter}{suffix}"
        if not target.exists():
            return target
        counter += 1


def category_for(path, move_others):
    ext = path.suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return None
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]
    return OTHERS if move_others else None


def list_files(folder, recursive, category_names):
    """Yield every regular file to consider, using os.scandir()."""
    try:
        with os.scandir(folder) as entries:
            entries = list(entries)
    except PermissionError:
        log.error(f"No permission to read folder: {folder}")
        return
    except OSError as err:
        log.error(f"Cannot read folder {folder}: {err}")
        return

    for entry in entries:
        try:
            if entry.is_symlink():
                continue
            if entry.is_file():
                yield Path(entry.path)
            elif recursive and entry.is_dir() and entry.name not in category_names:
                yield from list_files(entry.path, recursive, category_names)
        except OSError as err:
            log.error(f"Cannot inspect {entry.path}: {err}")


# ---------- Main logic ----------

def organize(folder, dry_run=False, recursive=False, move_others=False):
    folder = Path(folder).expanduser().resolve()
    stats = {"moved": 0, "skipped": 0, "errors": 0, "renamed": 0}
    per_category = {}

    if not folder.is_dir():
        log.error(f"Folder not found: {folder}")
        return stats, per_category

    log.info(f"Organizing: {folder}" + ("  [DRY RUN]" if dry_run else ""))
    category_names = set(CATEGORIES) | {OTHERS}

    for path in list_files(folder, recursive, category_names):
        # skip hidden files, this script and its log file
        if path.name.startswith(".") or path.resolve() in (
                Path(__file__).resolve(), LOG_FILE):
            stats["skipped"] += 1
            continue

        category = category_for(path, move_others)
        if category is None:
            stats["skipped"] += 1
            log.info(f"SKIP   {path.name}  (unknown or temporary type)")
            continue

        dest_dir = folder / category
        # Already sitting in the right category folder: nothing to do.
        if path.parent == dest_dir:
            stats["skipped"] += 1
            continue

        try:
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
            destination = unique_destination(dest_dir, path.name)
            renamed = destination.name != path.name

            if dry_run:
                log.info(f"WOULD MOVE  {path.name}  ->  {category}/{destination.name}")
            else:
                shutil.move(str(path), str(destination))
                log.info(f"MOVED  {path.name}  ->  {category}/{destination.name}")

            stats["moved"] += 1
            stats["renamed"] += int(renamed)
            per_category[category] = per_category.get(category, 0) + 1

        except PermissionError:
            stats["errors"] += 1
            log.error(f"PERMISSION DENIED  {path.name} (file may be open or protected)")
        except FileExistsError:
            stats["errors"] += 1
            log.error(f"ALREADY EXISTS  {path.name}")
        except OSError as err:
            stats["errors"] += 1
            log.error(f"ERROR  {path.name}: {err}")

    return stats, per_category


def print_summary(stats, per_category, dry_run):
    line = "=" * 44
    verb = "Would be moved" if dry_run else "Files moved"
    log.info("\n" + line)
    log.info(f"{'EXECUTION SUMMARY':^44}")
    log.info(line)
    for category in sorted(per_category):
        log.info(f"  {category:<12}{per_category[category]:>6}")
    log.info("-" * 44)
    log.info(f"  {verb:<22}{stats['moved']:>6}")
    log.info(f"  {'Renamed (name clash)':<22}{stats['renamed']:>6}")
    log.info(f"  {'Skipped':<22}{stats['skipped']:>6}")
    log.info(f"  {'Errors':<22}{stats['errors']:>6}")
    log.info(line)


def main():
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would be moved without moving anything")
    parser.add_argument("--recursive", action="store_true",
                        help="also organize files inside subfolders")
    parser.add_argument("--others", action="store_true",
                        help="move unknown file types into an 'Others' folder")
    args = parser.parse_args()

    setup_logging()
    stats, per_category = organize(args.folder, args.dry_run, args.recursive, args.others)
    print_summary(stats, per_category, args.dry_run)


if __name__ == "__main__":
    main()
