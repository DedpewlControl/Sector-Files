from pathlib import Path
import shutil
import zipfile
import tempfile
import fnmatch
import py7zr

from config import REPO_LAYOUT_MAP, GNG_ONLY_FILES, FIRS


def matches(path: Path, patterns: list[str]) -> bool:
    s = path.as_posix()
    return any(fnmatch.fnmatch(s, p) for p in patterns)


def extract_archive(archive: Path, dest: Path):
    out = dest / archive.stem
    out.mkdir(parents=True, exist_ok=True)

    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(out)
    elif archive.suffix.lower() == ".7z":
        with py7zr.SevenZipFile(archive, "r") as z:
            z.extractall(out)
    else:
        raise ValueError(f"Unsupported archive: {archive}")

    return out


def copy_tree(src: Path, dst: Path, exclude=None):
    for file in src.rglob("*"):
        if not file.is_file():
            continue

        rel = file.relative_to(src)

        if exclude and matches(rel, exclude):
            continue

        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)


def apply_repo_layout(repo_root: Path, install_root: Path):
    for src_rel, dst_rel in REPO_LAYOUT_MAP.items():
        src = repo_root / src_rel
        dst = install_root / dst_rel

        if src.exists():
            copy_tree(src, dst, exclude=GNG_ONLY_FILES)


def apply_gng_packages(packages: list[Path], install_root: Path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        for package in packages:
            extract_archive(package, tmp)

        for file in tmp.rglob("*"):
            if not file.is_file():
                continue

            for pattern in GNG_ONLY_FILES:
                for fir in FIRS + ["LFXX"]:
                    parts = file.parts
                    if fir in parts:
                        rel_index = parts.index(fir)
                        rel = Path(*parts[rel_index:])

                        if matches(rel, GNG_ONLY_FILES):
                            target = install_root / rel
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file, target)


def normalize_sectors(install_root: Path):
    sectors = install_root / "LFXX" / "Sectors"
    sectors.mkdir(parents=True, exist_ok=True)

    for file in list(sectors.iterdir()):
        if not file.is_file():
            continue

        if file.suffix.lower() not in [".sct", ".ese", ".rwy"]:
            continue

        upper = file.name.upper()

        for code in FIRS + ["LFFM", "LFXX"]:
            if upper.startswith(code):
                target_code = "LFXX" if code == "LFFM" else code
                target = sectors / f"{target_code}{file.suffix.lower()}"

                if file != target:
                    if target.exists():
                        target.unlink()
                    file.rename(target)
                break