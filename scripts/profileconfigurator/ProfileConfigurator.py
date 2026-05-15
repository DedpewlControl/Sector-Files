from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


APP_NAME = "CoFrance Profile Configurator"
GREEN = "#2d7d46"
AMBER = "#d08b00"
GRAY = "#777777"


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


def get_start_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def looks_like_controller_pack(path: Path) -> bool:
    return (
        (path / "LFXX").exists()
        and any((path / fir).exists() for fir in ["LFBB", "LFEE", "LFFF", "LFMM", "LFRR"])
    )


def find_prf_files(controller_pack_dir: Path) -> list[Path]:
    return sorted(controller_pack_dir.rglob("*.prf"))


def update_profiles(controller_pack_dir: Path) -> int:
    """
    Replace this section with your existing PRF update logic.

    IMPORTANT:
    Do not update sector file entries here anymore.
    Sector paths are now handled by the Installer.
    """

    prf_files = find_prf_files(controller_pack_dir)

    for prf in prf_files:
        text = prf.read_text(encoding="utf-8", errors="ignore")

        # Example placeholder:
        # text = text.replace("OLD_VALUE", "NEW_VALUE")

        # Remove/skip sector file edits here.
        # Do NOT write SectorFile / SectorFileName / Sector entries.

        prf.write_text(text, encoding="utf-8", errors="ignore")

    return len(prf_files)


class ProfileConfiguratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)

        icon_path = resource_path("ProfileConfigurator.ico")
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        self.root.geometry("700x430")
        self.root.resizable(False, False)

        self.controller_pack_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="No controller pack directory selected")
        self.prf_count_text = tk.StringVar(value="Profiles detected: 0")

        tk.Label(
            root,
            text="CoFrance Profile Configurator",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=14)

        tk.Label(
            root,
            text=(
                "Select your Controller Pack Directory to update profile login "
                "and configuration settings. Sector file paths are handled by the Installer."
            ),
            wraplength=640,
        ).pack(pady=4)

        tk.Button(
            root,
            text="Controller Pack Directory",
            command=self.select_controller_pack_directory,
            height=2,
        ).pack(fill="x", padx=40, pady=8)

        tk.Label(
            root,
            textvariable=self.controller_pack_dir,
            wraplength=640,
            fg="gray",
        ).pack()

        tk.Label(
            root,
            textvariable=self.prf_count_text,
            fg="gray",
        ).pack(pady=8)

        self.action_button = tk.Button(
            root,
            text="Update Profile Configuration",
            command=self.run_profile_update,
            height=2,
            bg=GREEN,
            fg="white",
        )
        self.action_button.pack(fill="x", padx=40, pady=18)

        tk.Label(
            root,
            textvariable=self.status_text,
            fg="gray",
            wraplength=640,
        ).pack()

        self.auto_detect_start_directory()
        self.refresh_status()

    def auto_detect_start_directory(self):
        start_dir = get_start_directory()

        if looks_like_controller_pack(start_dir):
            self.controller_pack_dir.set(str(start_dir))

    def refresh_status(self):
        if not self.controller_pack_dir.get():
            self.status_text.set("No controller pack directory selected")
            self.prf_count_text.set("Profiles detected: 0")
            self.action_button.config(bg=GRAY)
            return

        path = Path(self.controller_pack_dir.get())

        if not path.exists():
            self.status_text.set("Selected directory does not exist")
            self.prf_count_text.set("Profiles detected: 0")
            self.action_button.config(bg=GRAY)
            return

        if not looks_like_controller_pack(path):
            self.status_text.set("Selected folder does not look like a CoFrance controller pack")
            self.action_button.config(bg=AMBER)
        else:
            self.status_text.set("Ready")
            self.action_button.config(bg=GREEN)

        count = len(find_prf_files(path))
        self.prf_count_text.set(f"Profiles detected: {count}")

    def select_controller_pack_directory(self):
        folder = filedialog.askdirectory(
            title="Select controller pack directory"
        )

        if folder:
            self.controller_pack_dir.set(folder)
            self.refresh_status()

    def run_profile_update(self):
        if not self.controller_pack_dir.get():
            messagebox.showerror(
                "Missing directory",
                "Please select the controller pack directory first.",
            )
            return

        controller_pack_dir = Path(self.controller_pack_dir.get())

        try:
            self.root.config(cursor="wait")
            self.root.update_idletasks()

            updated_count = update_profiles(controller_pack_dir)

            self.refresh_status()

            messagebox.showinfo(
                "Complete",
                f"Profile configuration updated successfully.\n\nProfiles processed: {updated_count}",
            )

        except Exception as error:
            messagebox.showerror("Failed", str(error))

        finally:
            self.root.config(cursor="")
            self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = ProfileConfiguratorApp(root)
    root.mainloop()