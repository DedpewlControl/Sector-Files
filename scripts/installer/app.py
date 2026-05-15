from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import tempfile

from engine import apply_repo_layout, apply_gng_packages, normalize_sectors


class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CoFrance Installer")
        self.root.geometry("560x320")

        self.install_dir = tk.StringVar()
        self.gng_packages = []

        tk.Label(root, text="CoFrance Controller Pack Installer", font=("Segoe UI", 14, "bold")).pack(pady=12)

        tk.Button(root, text="Select Install Folder", command=self.select_install).pack(fill="x", padx=30, pady=5)
        tk.Label(root, textvariable=self.install_dir, wraplength=500).pack()

        tk.Button(root, text="Add GNG ZIP/7Z Packages", command=self.select_gng).pack(fill="x", padx=30, pady=5)

        self.package_label = tk.Label(root, text="No GNG packages selected")
        self.package_label.pack()

        tk.Button(root, text="Update from GitHub Repo Files", command=self.update_from_repo).pack(fill="x", padx=30, pady=18)

    def select_install(self):
        folder = filedialog.askdirectory(title="Select France install folder")
        if folder:
            self.install_dir.set(folder)

    def select_gng(self):
        files = filedialog.askopenfilenames(
            title="Select GNG packages",
            filetypes=[("Archive files", "*.zip *.7z")]
        )
        self.gng_packages = [Path(f) for f in files]
        self.package_label.config(text=f"{len(self.gng_packages)} GNG package(s) selected")

    def update_from_repo(self):
        if not self.install_dir.get():
            messagebox.showerror("Missing folder", "Please select the install folder.")
            return

        install_root = Path(self.install_dir.get())

        # app.py is scripts/installer/app.py, repo root is two levels up
        repo_root = Path(__file__).resolve().parents[2]

        try:
            apply_repo_layout(repo_root, install_root)

            if self.gng_packages:
                apply_gng_packages(self.gng_packages, install_root)

            normalize_sectors(install_root)

            messagebox.showinfo("Done", "Controller pack update complete.")

        except Exception as e:
            messagebox.showerror("Update failed", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()