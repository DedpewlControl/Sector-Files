from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from config import APP_NAME
from engine import update_controller_pack


class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("620x360")
        self.root.resizable(False, False)

        self.install_dir = tk.StringVar()
        self.gng_packages: list[Path] = []

        tk.Label(
            root,
            text="CoFrance Controller Pack Installer",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=14)

        tk.Label(
            root,
            text=(
                "Update from GitHub. Optionally select GNG ZIP/7Z packages "
                "to refresh AIRAC/generated files."
            ),
            wraplength=560,
        ).pack(pady=4)

        tk.Button(
            root,
            text="Select Installed France Folder",
            command=self.select_install_folder,
            height=2,
        ).pack(fill="x", padx=40, pady=8)

        tk.Label(
            root,
            textvariable=self.install_dir,
            wraplength=560,
            fg="gray",
        ).pack()

        tk.Button(
            root,
            text="Add Optional GNG ZIP/7Z Packages",
            command=self.select_gng_packages,
            height=2,
        ).pack(fill="x", padx=40, pady=8)

        self.gng_label = tk.Label(root, text="No GNG packages selected", fg="gray")
        self.gng_label.pack()

        tk.Button(
            root,
            text="Update Controller Pack",
            command=self.run_update,
            height=2,
            bg="#2d7d46",
            fg="white",
        ).pack(fill="x", padx=40, pady=22)

    def select_install_folder(self):
        folder = filedialog.askdirectory(
            title="Select installed France controller pack folder"
        )

        if folder:
            self.install_dir.set(folder)

    def select_gng_packages(self):
        files = filedialog.askopenfilenames(
            title="Select GNG update packages",
            filetypes=[
                ("Archive files", "*.zip *.7z"),
                ("ZIP files", "*.zip"),
                ("7Z files", "*.7z"),
            ],
        )

        self.gng_packages = [Path(file) for file in files]
        self.gng_label.config(
            text=f"{len(self.gng_packages)} GNG package(s) selected"
        )

    def run_update(self):
        if not self.install_dir.get():
            messagebox.showerror(
                "Missing install folder",
                "Please select the installed France folder first.",
            )
            return

        install_root = Path(self.install_dir.get())

        try:
            self.root.config(cursor="wait")
            self.root.update_idletasks()

            update_controller_pack(
                install_root=install_root,
                gng_packages=self.gng_packages,
            )

            messagebox.showinfo(
                "Update complete",
                "Controller pack update completed successfully.",
            )

        except Exception as error:
            messagebox.showerror(
                "Update failed",
                str(error),
            )

        finally:
            self.root.config(cursor="")
            self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()