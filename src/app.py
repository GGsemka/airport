import csv
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from dialogs import LoginDialog
from storage import BASE_DIR, AirportManager
from tabs import AirlinesTab, FlightsTab, GatesTab
from theme import Theme

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_SIZE = (160, 70)
CSV_TYPES = [("CSV files", "*.csv"), ("All files", "*.*")]


class AirportApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.manager = AirportManager()

    # Заголовок с Фамилией и Вариантом (п. 2.1)
    self.title("Веселовский С. Н. — Вариант 11 | Аэропорт: учет рейсов")
    self.geometry("1100x750")
    self.minsize(900, 600)

    Theme.apply(self)
    self._load_images()
    self._build_menu()
    self._build_ui()
    self._apply_auth_state()
    self.refresh_all()

  @property
  def is_authorized(self):
    return self.manager.is_authenticated

  # ---------- Иконка и логотип ----------

  def _load_images(self):
    self._icon = None
    self.logo_image = None

    icon_path = os.path.join(ASSETS_DIR, "icon.png")
    try:
      self._icon = tk.PhotoImage(file=icon_path)
      self.iconphoto(True, self._icon)
    except tk.TclError:
      pass
    if sys.platform.startswith("win"):
      try:
        self.iconbitmap(os.path.join(ASSETS_DIR, "icon.ico"))
      except tk.TclError:
        pass

    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    try:
      from PIL import Image, ImageTk  # необязательная зависимость

      resample = getattr(Image, "Resampling", Image).LANCZOS
      image = Image.open(logo_path).convert("RGBA").resize(LOGO_SIZE, resample)
      self.logo_image = ImageTk.PhotoImage(image)
    except ImportError:
      try:
        self.logo_image = tk.PhotoImage(file=logo_path)
      except tk.TclError:
        pass
    except OSError:
      pass

  # ---------- Интерфейс ----------

  def _build_menu(self):
    menubar = tk.Menu(self)
    self.file_menu = tk.Menu(menubar, tearoff=0)
    self.file_menu.add_command(label="Открыть...", command=self.open_csv)
    self.file_menu.add_command(label="Сохранить как...", command=self.save_csv)
    self.file_menu.add_separator()
    self.file_menu.add_command(label="Выход", command=self.destroy)
    menubar.add_cascade(label="Файл", menu=self.file_menu)
    self.config(menu=menubar)

  def _build_ui(self):
    # Строка состояния создаётся первой, чтобы всегда оставаться внизу
    self.status_bar = tk.Label(
        self,
        text="",
        bg="#CFD8DC",
        fg="#37474F",
        font=Theme.FONT_TABLE,
        bd=0,
        anchor=tk.W,
        padx=12,
        pady=6,
    )
    self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    top_frame = ttk.Frame(self)
    top_frame.pack(fill="x", padx=15, pady=(10, 6))
    self.btn_login = ttk.Button(
        top_frame, text="Войти", command=self.open_login_dialog
    )
    self.btn_login.pack(side=tk.LEFT, anchor="n")
    if self.logo_image:
      tk.Label(
          top_frame, image=self.logo_image, bd=0, bg=Theme.BG
      ).pack(side=tk.RIGHT)
    else:
      # Запас под логотип, чтобы вёрстка не зависела от наличия файла
      tk.Frame(top_frame, width=LOGO_SIZE[0], height=LOGO_SIZE[1],
               bg=Theme.BG).pack(side=tk.RIGHT)

    self.notebook = ttk.Notebook(self)
    self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    self.tab_flights = FlightsTab(self.notebook, self)
    self.tab_airlines = AirlinesTab(self.notebook, self)
    self.tab_gates = GatesTab(self.notebook, self)
    self.tabs = (self.tab_flights, self.tab_airlines, self.tab_gates)

    self.notebook.add(self.tab_flights, text="  Рейсы  ")
    self.notebook.add(self.tab_airlines, text="  Авиакомпании  ")
    self.notebook.add(self.tab_gates, text="  Гейты  ")
    self.notebook.select(self.tab_flights)  # активна по умолчанию

  # ---------- Состояние авторизации ----------

  def _apply_auth_state(self):
    authorized = self.is_authorized
    state = "normal" if authorized else "disabled"
    self.file_menu.entryconfig(0, state=state)
    self.file_menu.entryconfig(1, state=state)
    for tab in self.tabs:
      tab.set_authorized(authorized)
    if authorized:
      self.status_bar.config(
          text=f" Статус: Авторизован — {self.manager.current_user}",
          fg="#2E7D32",
      )
      self.btn_login.config(state="disabled")
    else:
      self.status_bar.config(
          text=" Статус: Гость | Не авторизован", fg="#37474F"
      )
      self.btn_login.config(state="normal")

  def refresh_all(self, select=None):
    for tab in self.tabs:
      tab.refresh(select)

  def open_login_dialog(self):
    if LoginDialog(self, self.manager).show():
      self._apply_auth_state()

  # ---------- CSV ----------

  def open_csv(self):
    if not self.is_authorized:
      return
    file_path = filedialog.askopenfilename(
        parent=self, filetypes=CSV_TYPES
    )
    if not file_path:
      return
    if self.manager.flights and not messagebox.askyesno(
        "Загрузка",
        "Текущие рейсы будут заменены данными из файла. Продолжить?",
        parent=self,
    ):
      return
    try:
      report = self.manager.load_from_csv(file_path)
    except (OSError, UnicodeDecodeError, csv.Error) as e:
      messagebox.showerror(
          "Ошибка", f"Не удалось прочитать файл:\n{e}", parent=self
      )
      return
    self.refresh_all()

    lines = [f"Загружено рейсов: {report.loaded}"]
    if report.created_airlines:
      lines.append(
          f"Создано авиакомпаний: {report.created_airlines} "
          "(страна и телефон не указаны в CSV)"
      )
    if report.created_gates:
      lines.append(
          f"Создано гейтов: {report.created_gates} (вместимость в CSV "
          "отсутствует — подобрана по числу пассажиров, проверьте её "
          "на вкладке «Гейты»)"
      )
    if report.errors:
      lines.append(f"\nПропущено строк: {len(report.errors)}")
      lines.extend(report.errors[:10])
      if len(report.errors) > 10:
        lines.append("...")
      messagebox.showwarning("Загрузка завершена", "\n".join(lines), parent=self)
    else:
      messagebox.showinfo("Загрузка завершена", "\n".join(lines), parent=self)

  def save_csv(self):
    if not self.is_authorized:
      return
    file_path = filedialog.asksaveasfilename(
        parent=self, defaultextension=".csv", filetypes=CSV_TYPES
    )
    if not file_path:
      return
    try:
      self.manager.save_to_csv(file_path)
    except OSError as e:
      messagebox.showerror(
          "Ошибка", f"Не удалось сохранить файл:\n{e}", parent=self
      )
      return
    messagebox.showinfo("Успех", "Данные успешно сохранены", parent=self)
