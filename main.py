import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
import time
import psutil
import win32gui
import win32con
import win32process
import winreg
import json

# Для работы с виртуальными рабочими столами
try:
    import pyvda  # pip install pyvda
    HAS_PYVDA = True
except ImportError:
    HAS_PYVDA = False

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

def delete_positions_from_registry(folder_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, folder_name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

class FolderBlock:
    def __init__(self, parent, folder_name, remove_callback):
        self.folder_name = folder_name
        self.folder = folder_name
        self.remove_callback = remove_callback

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.frame = tk.LabelFrame(
            parent,
            labelwidget=tk.Label(
                parent,
                text=folder_name,
                font=('TkDefaultFont', 10, 'bold')
            ),
            padx=8,
            pady=8
        )
        self.frame.grid_propagate(False)

        btn_save = tk.Button(self.frame, text="Save positions", width=17,
                             command=self.save_positions)
        btn_save.pack(pady=2)
        btn_restore = tk.Button(self.frame, text="Restore positions", width=17,
                                command=self.restore_positions)
        btn_restore.pack(pady=2)
        btn_open = tk.Button(self.frame, text="Open", width=17,
                             command=self.open_all)
        btn_open.pack(pady=2)
        btn_close_windows = tk.Button(self.frame, text="Close windows", width=17, fg="red",
                                      command=self.close_nomachine_windows)
        btn_close_windows.pack(pady=2)
        btn_toggle = tk.Button(self.frame, text="Minimize/Restore", width=17,
                               command=self.toggle_windows)
        btn_toggle.pack(pady=2)
        btn_remove = tk.Button(self.frame, text="✖", width=3, fg="red",
                               command=self.remove_block)
        btn_remove.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

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

    def get_window_desktop_num(self, hwnd):
        if HAS_PYVDA:
            try:
                return pyvda.GetWindowDesktopNumber(hwnd)
            except Exception:
                return None
        return None

    def move_window_to_desktop(self, hwnd, desktop_num):
        if HAS_PYVDA:
            try:
                pyvda.MoveWindowToDesktopNumber(hwnd, desktop_num)
            except Exception:
                pass

    def save_positions(self):
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        positions = {}
        for hwnd, session_title, title in hwnds:
            rect = win32gui.GetWindowRect(hwnd)
            desktop_num = self.get_window_desktop_num(hwnd)
            positions[session_title] = {
                'hwnd': hwnd,
                'window_title': title,
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3],
                'desktop_num': desktop_num
            }
        save_positions_to_registry(self.folder_name, positions)

    def restore_positions(self):
        positions = load_positions_from_registry(self.folder_name)
        if not positions:
            return
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        for hwnd, session_title, _ in hwnds:
            pos = positions.get(session_title)
            if pos:
                # Перемещаем окно на нужный виртуальный рабочий стол, если pyvda доступна
                if HAS_PYVDA and 'desktop_num' in pos and pos['desktop_num'] is not None:
                    current_desk = pyvda.GetWindowDesktopNumber(hwnd)
                    if current_desk != pos['desktop_num']:
                        self.move_window_to_desktop(hwnd, pos['desktop_num'])
                        time.sleep(0.1)
                win32gui.MoveWindow(
                    hwnd,
                    pos['left'],
                    pos['top'],
                    pos['right'] - pos['left'],
                    pos['bottom'] - pos['top'],
                    True
                )

    def open_all(self):
        if not os.path.isdir(self.folder):
            return
        nxs_files = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.lower().endswith('.nxs')]
        titles = self.get_nxs_titles()
        # Получим уже открытые окна NoMachine по этим тайтлам
        opened_titles = [session_title for _, session_title, _ in self.get_nomachine_windows_by_titles(titles)]
        for nxs in nxs_files:
            session_title = os.path.splitext(os.path.basename(nxs))[0]
            if session_title not in opened_titles:
                try:
                    os.startfile(nxs)
                except Exception:
                    pass
                time.sleep(0.5)

    def close_nomachine_windows(self):
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        for hwnd, session_title, title in hwnds:
            try:
                win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
            except Exception:
                pass

    def is_minimized(self, hwnd):
        return win32gui.IsIconic(hwnd)

    def toggle_windows(self):
        titles = self.get_nxs_titles()
        hwnds = self.get_nomachine_windows_by_titles(titles)
        if not hwnds:
            return
        minimized = [hwnd for hwnd, _, _ in hwnds if self.is_minimized(hwnd)]
        not_minimized = [hwnd for hwnd, _, _ in hwnds if not self.is_minimized(hwnd)]

        if len(minimized) == len(hwnds):
            # Все свернуты — развернуть все
            for hwnd, _, _ in hwnds:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                except Exception:
                    pass
        elif len(not_minimized) == len(hwnds):
            # Все развернуты — свернуть все
            for hwnd, _, _ in hwnds:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                except Exception:
                    pass
        else:
            # Часть свернута, часть нет — развернуть только свернутые
            for hwnd in minimized:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                except Exception:
                    pass

    def remove_block(self):
        if messagebox.askyesno("Remove block", f"Remove block '{self.folder_name}'?\n(The folder and files will not be deleted)"):
            self.frame.destroy()
            self.remove_callback(self.folder_name)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NoMachine Workspace Manager")
        # Запрещаем изменять размер окна
        self.root.resizable(False, False)

        self.blocks = {}
        self.blocks_list = []
        self.top_panel = tk.Frame(root)
        self.top_panel.pack(fill="x", pady=2)

        self.btn_add = tk.Button(self.top_panel, text="+", width=3, fg="green", command=self.add_folder_dialog)
        self.btn_add.pack(side="right", padx=5)

        self.blocks_frame = tk.Frame(root)
        self.blocks_frame.pack(fill="both", expand=True)

        self.folder_list = load_folders_list()
        if self.folder_list:
            for folder in self.folder_list:
                self.add_folder_block(folder, save=False)
            self.update_window_size()
        else:
            self.ask_and_create_first_block()

    def save_folders(self):
        save_folders_list(list(self.blocks.keys()))

    def ask_and_create_first_block(self):
        folder_name = simpledialog.askstring("Folder name", "Enter the name for the first folder:")
        if folder_name:
            self.add_folder_block(folder_name)
            self.update_window_size()
        else:
            messagebox.showerror("Error", "Folder name not provided. Exiting.")
            self.root.destroy()

    def add_folder_dialog(self):
        folder_name = simpledialog.askstring("Folder name", "Enter new folder name:")
        if not folder_name:
            return
        if folder_name in self.blocks:
            return
        self.add_folder_block(folder_name)
        self.save_folders()
        self.update_window_size()

    def add_folder_block(self, folder_name, save=True):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        block = FolderBlock(self.blocks_frame, folder_name, self.remove_block)
        self.blocks[folder_name] = block
        self.blocks_list.append(block)
        self.arrange_blocks()
        if save:
            self.save_folders()

    def remove_block(self, folder_name):
        if folder_name in self.blocks:
            delete_positions_from_registry(folder_name)
            self.blocks_list.remove(self.blocks[folder_name])
            del self.blocks[folder_name]
            self.arrange_blocks()
            self.save_folders()
            self.update_window_size()

    def arrange_blocks(self):
        min_block_width = 220
        min_block_height = 130
        padding = 16
        # Два столбца, если больше 3 блоков, иначе один
        if len(self.blocks_list) <= 3:
            cols = 1
        else:
            cols = 2
        block_width = min_block_width

        for idx, block in enumerate(self.blocks_list):
            row = idx // cols
            col = idx % cols
            block.frame.config(width=block_width)
            block.frame.grid(row=row, column=col, padx=padding//2, pady=padding//2, sticky="nsew")
        for c in range(cols):
            self.blocks_frame.grid_columnconfigure(c, weight=1)
        for r in range((len(self.blocks_list)+cols-1)//cols):
            self.blocks_frame.grid_rowconfigure(r, weight=1)

        self._current_cols = cols

    def update_window_size(self):
        self.root.update_idletasks()
        if not self.blocks_list:
            self.root.geometry("300x200")
            return
        block_w = self.blocks_list[0].frame.winfo_reqwidth()
        block_h = self.blocks_list[0].frame.winfo_reqheight()
        padding = 16
        cols = getattr(self, "_current_cols", 1)
        rows = (len(self.blocks_list) + cols - 1) // cols
        min_width = block_w * cols + padding * (cols + 1) + 40
        min_height = block_h * rows + padding * (rows + 1) + 100
        self.root.geometry(f"{min_width}x{min_height}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x250")
    app = App(root)
    root.mainloop()
