# NoMachine Workspace Manager

- [English](#english)
- [Русский](#русский)

---

## English

**NoMachine Workspace Manager** is a utility for organizing and managing NoMachine windows launched from `.nxs` files, with saving and restoring window positions. All settings are stored in the Windows Registry — no extra files are created next to the `.exe`.

### Features

- **Work with multiple folders:**  
  Each folder can contain its own `.nxs` NoMachine connection files. For each folder, a separate control block is created.
- **Save window positions:**  
  Remembers the positions and sizes of all NoMachine windows corresponding to `.nxs` files from the selected folder.
- **Restore window positions:**  
  Restores all NoMachine windows to their previously saved positions.
- **Open all connections from a folder:**  
  Instantly launches all `.nxs` files from a folder.
- **Close all NoMachine windows for a folder:**  
  Quickly closes all NoMachine windows related to the chosen folder.
- **Remove a block:**  
  Removes the folder block from the program and deletes its settings from the registry (but the folder and files remain on disk).

### How it works

1. On the first launch, enter the name of a folder with `.nxs` files (for example, `Days` or `Projects`).  
   You can add multiple folders (via the "+" button).
2. For each folder, you have controls:
   - **Save positions** — save the current positions of all relevant NoMachine windows (stores to registry).
   - **Restore positions** — move windows to their saved positions.
   - **Open** — open all connections from the folder.
   - **Close windows** — close all related NoMachine windows.
   - **✖** — remove the block (removes settings from registry, but not files/folder).

### Advantages

- **No extra files** — all settings are stored in the Windows Registry:  
  `HKEY_CURRENT_USER\Software\NoMachineWorkspaceManager`
- **Works from any folder** — you can run the program from anywhere, settings are always automatically loaded for the current Windows user.
- **Safe** — removing a block never deletes your `.nxs` files.

### Usage

1. Place `NoMachineWorkspaceManager.exe`.
2. Run the program.
3. Follow the interface: add working folders, open/close/save window positions as needed.

### Notes

- The program only works with NoMachine windows (`nxplayer.exe`) that were opened via `.nxs` files from the specified folders.
- Settings are separate for each Windows user.
- When a block is removed, all its registry settings are deleted — but your files on disk remain.

---

## Русский

**NoMachine Workspace Manager** — это утилита для удобной организации и управления окнами NoMachine, открываемыми из `.nxs`-файлов, с возможностью сохранения и восстановления их расположения на экране. Все настройки хранятся в реестре Windows — рядом с `.exe` никаких лишних файлов не создаётся.

### Возможности

- **Работа с несколькими рабочими папками:**  
  Каждая папка содержит свои `.nxs`-файлы (подключения NoMachine). Для каждой папки создаётся отдельный блок управления.
- **Сохранение позиций окон:**  
  Программа запоминает расположение и размер всех окон NoMachine, соответствующих `.nxs`-файлам из выбранной папки.
- **Восстановление расположения:**  
  Одним кликом восстанавливает окна NoMachine на те позиции, где они были сохранены.
- **Открытие всех подключений из папки:**  
  Быстрое открытие всех `.nxs`-файлов из папки в один клик.
- **Закрытие всех окон NoMachine для папки:**  
  Быстрое закрытие всех окон, относящихся к выбранной папке.
- **Удаление блока:**  
  Удаляет блок из программы и настройки для этой папки из реестра, но файлы и папка на диске остаются.

### Как работает

1. При первом запуске укажите имя папки с `.nxs`-файлами (например, `Days` или `Projects`).  
   Можно добавить несколько папок (кнопка "+").
2. Для каждой папки доступны кнопки:
   - **Save positions** — сохранить позиции окон (сохраняется в реестр).
   - **Restore positions** — восстановить сохранённые позиции.
   - **Open** — открыть все подключения из папки.
   - **Close windows** — закрыть все окна NoMachine, связанные с этой папкой.
   - **✖** — удалить блок (настройки для папки будут удалены из реестра, но папка и файлы останутся).

### Преимущества

- **Не создаёт лишних файлов рядом с .exe** — все настройки хранятся в реестре Windows:  
  `HKEY_CURRENT_USER\Software\NoMachineWorkspaceManager`
- **Работает из любой папки** — можно запускать программу из любой папки или с флешки, настройки всегда будут подхватываться автоматически для текущего пользователя Windows.
- **Безопасно** — удаление блока не трогает ваши `.nxs`-файлы.

### Запуск

1. Поместите `NoMachineWorkspaceManager.exe` в любую удобную папку.
2. Запустите программу.
3. Следуйте инструкциям интерфейса: добавьте рабочие папки, открывайте/закрывайте/сохраняйте позиции окон NoMachine.

### Важно

- Программа работает только с окнами NoMachine (`nxplayer.exe`), которые были открыты через `.nxs`-файлы из указанных папок.
- Настройки хранятся отдельно для каждого пользователя Windows.
- При удалении блока из программы все настройки для этой папки будут удалены из реестра, но файлы на диске останутся.

---
