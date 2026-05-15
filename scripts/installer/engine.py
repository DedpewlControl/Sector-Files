from pathlib import Path
import fnmatch
import shutil
import tempfile
import zipfile

import py7zr
import requests

from config import (
    FIRS,
    REPO_LAYOUT_MAP,
    GNG_ONLY_FILES,
    GITHUB_OWNER,
    GITHUB_REPO,
    GITHUB_BRANCH,
)


def matches(path: Path, patterns: list[str]) -> bool:
    normalized = path.as_posix()
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def download_github_repo() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="cofrance_repo_"))
    zip_path = tmp / "repo.zip"

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/zipball/{GITHUB_BRANCH}"

    response = requests.get(url, allow_redirects=True, timeout=60)
    response.raise_for_status()
    zip_path.write_bytes(response.content)

    extract_dir = tmp / "repo"
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(extract_dir)

    repo_root = next(path for path in extract_dir.iterdir() if path.is_dir())
    return repo_root


def extract_archive(archive: Path, destination: Path) -> Path:
    output = destination / archive.stem
    output.mkdir(parents=True, exist_ok=True)

    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(output)

    elif archive.suffix.lower() == ".7z":
        with py7zr.SevenZipFile(archive, "r") as z:
            z.extractall(output)

    else:
        raise ValueError(f"Unsupported archive type: {archive}")

    return output


def sync_tree(src: Path, dst: Path, exclude: list[str] | None = None):
    dst.mkdir(parents=True, exist_ok=True)

    for existing in sorted(dst.rglob("*"), reverse=True):
        rel = existing.relative_to(dst)

        if exclude and matches(rel, exclude):
            continue

        source_equivalent = src / rel

        if not source_equivalent.exists():
            if existing.is_dir():
                shutil.rmtree(existing, ignore_errors=True)
            else:
                existing.unlink()

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
            sync_tree(src, dst, exclude=GNG_ONLY_FILES)


def detect_sector_code(filename: str) -> str | None:
    upper = filename.upper()

    for code in FIRS + ["LFFM", "LFXX"]:
        if upper.startswith(code):
            return "LFXX" if code == "LFFM" else code

    return None


def apply_gng_packages(packages: list[Path], install_root: Path):
    sector_dir = install_root / "LFXX" / "Sector"
    sector_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cofrance_gng_") as tmp_name:
        tmp = Path(tmp_name)

        for package in packages:
            extract_archive(package, tmp)

        for file in tmp.rglob("*"):
            if not file.is_file():
                continue

            suffix = file.suffix.lower()

            if suffix in [".sct", ".ese", ".rwy"]:
                code = detect_sector_code(file.name)

                if code:
                    target = sector_dir / f"{code}{suffix}"

                    if target.exists():
                        target.unlink()

                    shutil.copy2(file, target)

                continue

            parts = file.parts

            for code in FIRS + ["LFXX", "LFFM"]:
                if code in parts:
                    index = parts.index(code)
                    rel = Path(*parts[index:])

                    if rel.parts[0] == "LFFM":
                        rel = Path("LFXX", *rel.parts[1:])

                    if matches(rel, GNG_ONLY_FILES):
                        target = install_root / rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file, target)

                    break


def normalize_sectors(install_root: Path):
    sector_dir = install_root / "LFXX" / "Sector"
    sector_dir.mkdir(parents=True, exist_ok=True)

    for file in list(sector_dir.iterdir()):
        if not file.is_file():
            continue

        if file.suffix.lower() not in [".sct", ".ese", ".rwy"]:
            continue

        code = detect_sector_code(file.name)

        if not code:
            continue

        target = sector_dir / f"{code}{file.suffix.lower()}"

        if file.resolve() != target.resolve():
            if target.exists():
                target.unlink()
            file.rename(target)


def update_controller_pack(
    install_root: Path,
    gng_packages: list[Path] | None = None,
):
    repo_root = download_github_repo()

    apply_repo_layout(repo_root, install_root)

    if gng_packages:
        apply_gng_packages(gng_packages, install_root)

    normalize_sectors(install_root)