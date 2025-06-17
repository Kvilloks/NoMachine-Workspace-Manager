import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
import time
import psutil
import win32gui
import win32process
import winreg
import json

REG_PATH = r"Software\NoMachineWorkspaceManager"

def save_positions_to_registry(folder_name, data):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    winreg.SetValueEx(key, folder_name, 0, winreg.REG_SZ, json.dumps(data))
    winreg.CloseKey(key)

def load_positions_from_registry(folder_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, folder_name)
        winreg.CloseKey(key)
        return json.loads(value)
    except FileNotFoundError:
        return None

def save_folders_list(folders):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    winreg.SetValueEx(key, "_folders", 0, winreg.REG_SZ, json.dumps(folders))
    winreg.CloseKey(key)

def load_folders_list():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, "_folders")
        winreg.CloseKey(key)
        return json.loads(value)
    except FileNotFoundError:
        return []

class FolderBlock:
    def __init__(self, parent, folder_name, remove_callback):
        self.folder_name = folder_name
        self.folder = folder_name
        self.remove_callback = remove_callback

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.frame = tk.LabelFrame(parent, text=folder_name, padx=10, pady=10)
        self.frame.pack(fill="both", expand="yes", padx=10, pady=5)

        btn_save = tk.Button(self.frame, text="Save positions", width=30,
                             command=self.save_positions)
        btn_save.pack(pady=2)
        btn_restore = tk.Button(self.frame, text="Restore positions", width=30,
                                command=self.restore_positions)
        btn_restore.pack(pady=2)
        btn_open = tk.Button(self.frame, text="Open", width=30,
                             command=self.open_all)
        btn_open.pack(pady=2)
        btn_close_windows = tk.Button(self.frame, text="Close windows", width=30, fg="red",
                                      command=self.close_nomachine_windows)
        btn_close_windows.pack(pady=2)
        btn_remove = tk.Button(self.frame, text="✖", width=3, fg="red",
                               command=self.remove_block)
        btn_remove.pack(side="right", anchor="ne", padx=2, pady=2)

    def get_nxs_titles(self):
        if not os.path.isdir(self.folder):
            return []
        return [os.path.splitext(f)[0] for f in os.listdir(self.folder) if f.lower().endswith('.nxs')]

    def get_nomachine_windows_by_titles(self, titles):
        hwnds = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    if proc.name().lower().startswith('nxplayer'):
                        for session_title in titles:
                            if session_title in title:
                                hwnds.append((hwnd, session_title, title))
                except Exception:
                    pass
            return True
        win32gui.EnumWindows(callback, None)
        return hwnds

    def save_positions(self):
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        positions = {}
        for hwnd, session_title, title in hwnds:
            rect = win32gui.GetWindowRect(hwnd)
            positions[session_title] = {
                'hwnd': hwnd,
                'window_title': title,
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3]
            }
        save_positions_to_registry(self.folder_name, positions)
        messagebox.showinfo("Saved", f"Positions saved in Windows Registry")

    def restore_positions(self):
        positions = load_positions_from_registry(self.folder_name)
        if not positions:
            messagebox.showerror("Error", f"No saved positions in registry for {self.folder_name}")
            return
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        for hwnd, session_title, _ in hwnds:
            pos = positions.get(session_title)
            if pos:
                win32gui.MoveWindow(
                    hwnd,
                    pos['left'],
                    pos['top'],
                    pos['right'] - pos['left'],
                    pos['bottom'] - pos['top'],
                    True
                )
        messagebox.showinfo("Restored", f"Window positions restored from registry")

    def open_all(self):
        if not os.path.isdir(self.folder):
            messagebox.showerror("Error", f"Folder not found: {self.folder}")
            return
        nxs_files = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.lower().endswith('.nxs')]
        for nxs in nxs_files:
            try:
                os.startfile(nxs)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open {nxs}:\n{e}")
            time.sleep(0.5)
        messagebox.showinfo("Opened", f"All NoMachine windows from folder '{self.folder}' have been opened.")

    def close_nomachine_windows(self):
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        closed = 0
        for hwnd, session_title, title in hwnds:
            try:
                win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                closed += 1
            except Exception:
                pass
        messagebox.showinfo("Closed", f"Closed {closed} NoMachine windows for folder '{self.folder}'.")

    def remove_block(self):
        if messagebox.askyesno("Remove block", f"Remove block '{self.folder_name}'?\n(The folder and files will not be deleted)"):
            self.frame.destroy()
            self.remove_callback(self.folder_name)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NoMachine Workspace Manager")
        self.blocks = {}
        self.top_panel = tk.Frame(root)
        self.top_panel.pack(fill="x", pady=2)
        self.btn_add = tk.Button(self.top_panel, text="+", width=3, fg="green", command=self.add_folder_dialog)
        self.btn_add.pack(side="right", padx=5)
        self.xtra_widgets_frame = tk.Frame(root)
        self.xtra_widgets_frame.pack(fill="both", expand=True)
        self.folder_list = load_folders_list()
        if self.folder_list:
            for folder in self.folder_list:
                self.add_folder_block(folder, save=False)
        else:
            self.ask_and_create_first_block()

    def save_folders(self):
        save_folders_list(list(self.blocks.keys()))

    def ask_and_create_first_block(self):
        folder_name = simpledialog.askstring("Folder name", "Enter the name for the first folder:")
        if folder_name:
            self.add_folder_block(folder_name)
        else:
            messagebox.showerror("Error", "Folder name not provided. Exiting.")
            self.root.destroy()

    def add_folder_dialog(self):
        folder_name = simpledialog.askstring("Folder name", "Enter new folder name:")
        if not folder_name:
            return
        if folder_name in self.blocks:
            messagebox.showerror("Exists", f"Block for '{folder_name}' already exists!")
            return
        self.add_folder_block(folder_name)
        self.save_folders()

    def add_folder_block(self, folder_name, save=True):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        block = FolderBlock(self.root, folder_name, self.remove_block)
        self.blocks[folder_name] = block
        if save:
            self.save_folders()

    def remove_block(self, folder_name):
        if folder_name in self.blocks:
            del self.blocks[folder_name]
            self.save_folders()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()