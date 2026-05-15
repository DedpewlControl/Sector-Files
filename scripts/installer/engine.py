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
    VERSION_FILE,
)


COPYRIGHT_FILE = "aeronav_copyright.txt"

try:
    from build_info import BUILD_COMMIT
except Exception:
    BUILD_COMMIT = "dev"


def matches(path: Path, patterns: list[str]) -> bool:
    normalized = path.as_posix()
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def get_github_version() -> str:
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()["sha"][:7]


def get_local_version(install_root: Path) -> str:
    version_file = install_root / VERSION_FILE

    if version_file.exists():
        return version_file.read_text(encoding="utf-8", errors="ignore").strip()

    return "Not installed"


def write_installed_version(install_root: Path, version: str):
    version_file = install_root / VERSION_FILE
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(version, encoding="utf-8")


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

    return next(path for path in extract_dir.iterdir() if path.is_dir())


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

        if not (src / rel).exists():
            if existing.is_dir():
                shutil.rmtree(existing, ignore_errors=True)
            else:
                existing.unlink()

    for file in src.rglob("*"):
        if not file.is_file():
            continue

        if file.name.lower() == COPYRIGHT_FILE:
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


def should_skip_sector_file(file: Path) -> bool:
    upper = file.name.upper()
    return upper.startswith("LFFM") and file.suffix.lower() == ".sct"


def copy_single_copyright_file(source_root: Path, install_root: Path):
    target = install_root / COPYRIGHT_FILE

    if target.exists():
        return

    for file in source_root.rglob(COPYRIGHT_FILE):
        if file.is_file():
            shutil.copy2(file, target)
            return


def remove_duplicate_copyright_files(install_root: Path):
    root_copy = install_root / COPYRIGHT_FILE

    for file in install_root.rglob(COPYRIGHT_FILE):
        if file.resolve() == root_copy.resolve():
            continue
        file.unlink()


def apply_gng_packages(packages: list[Path], install_root: Path):
    sector_dir = install_root / "LFXX" / "Sectors"
    sector_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cofrance_gng_") as tmp_name:
        tmp = Path(tmp_name)

        for package in packages:
            extract_archive(package, tmp)

        copy_single_copyright_file(tmp, install_root)

        for file in tmp.rglob("*"):
            if not file.is_file():
                continue

            if file.name.lower() == COPYRIGHT_FILE:
                continue

            suffix = file.suffix.lower()

            if suffix in [".sct", ".ese", ".rwy"]:
                if should_skip_sector_file(file):
                    continue

                code = detect_sector_code(file.name)

                if code:
                    target = sector_dir / f"{code}{suffix}"
                    if target.exists():
                        target.unlink()
                    shutil.copy2(file, target)

                continue

            parts = file.parts

            for fir in FIRS:
                if fir in parts:
                    index = parts.index(fir)
                    rel = Path(*parts[index:])

                    if matches(rel, GNG_ONLY_FILES):
                        target = install_root / rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file, target)

                    break

    remove_duplicate_copyright_files(install_root)


def normalize_sectors(install_root: Path):
    sector_dir = install_root / "LFXX" / "Sector"
    sector_dir.mkdir(parents=True, exist_ok=True)

    for file in list(sector_dir.iterdir()):
        if not file.is_file():
            continue

        if file.suffix.lower() not in [".sct", ".ese", ".rwy"]:
            continue

        if should_skip_sector_file(file):
            file.unlink()
            continue

        code = detect_sector_code(file.name)

        if not code:
            continue

        target = sector_dir / f"{code}{file.suffix.lower()}"

        if file.resolve() != target.resolve():
            if target.exists():
                target.unlink()
            file.rename(target)


def cleanup_legacy_root_files(install_root: Path):
    allowed_root_files = {
        "aeronav_copyright.txt",
        "ProfileConfigurator.exe",
    }

    for item in install_root.iterdir():
        if item.is_dir():
            if item.name.upper() == "EXE":
                shutil.rmtree(item, ignore_errors=True)
            continue

        if item.name in allowed_root_files:
            continue

        if item.suffix.lower() in [".sct", ".ese", ".rwy", ".prf"]:
            item.unlink()


def cleanup_install(install_root: Path):
    remove_duplicate_copyright_files(install_root)
    cleanup_legacy_root_files(install_root)

    sector_dir = install_root / "LFXX" / "Sector"

    for bad_name in ["LFFM.sct", "LFXX.sct"]:
        bad_file = sector_dir / bad_name
        if bad_file.exists():
            bad_file.unlink()


def update_controller_pack(
    install_root: Path,
    gng_packages: list[Path] | None = None,
):
    github_version = get_github_version()
    repo_root = download_github_repo()

    apply_repo_layout(repo_root, install_root)

    if gng_packages:
        apply_gng_packages(gng_packages, install_root)

    normalize_sectors(install_root)
    cleanup_install(install_root)
    write_installed_version(install_root, github_version)