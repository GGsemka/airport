"""Оформление приложения (п. 2.2 задания)."""

from tkinter import ttk


class Theme:
  BG = "#ECEFF1"          # фон окна
  TAB_BG = "#0D47A1"      # фон панели вкладок
  TAB_FG = "#BBDEFB"      # текст вкладок
  BTN_BG = "#1565C0"      # фон кнопок
  BTN_FG = "#FFFFFF"      # текст кнопок
  TEXT = "#263238"

  FONT_TABLE = ("Tahoma", 9)
  FONT_HEADING = ("Tahoma", 14, "bold")
  FONT_BUTTON = ("Tahoma", 10)
  FONT_LABEL = ("Tahoma", 10)

  @classmethod
  def apply(cls, root):
    root.configure(bg=cls.BG)
    root.option_add("*TCombobox*Listbox.font", cls.FONT_LABEL)
    root.option_add("*TCombobox*Listbox.selectBackground", cls.BTN_BG)
    root.option_add("*TCombobox*Listbox.selectForeground", cls.BTN_FG)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=cls.BG)
    style.configure(
        "TLabel", background=cls.BG, foreground=cls.TEXT, font=cls.FONT_LABEL
    )
    style.configure(
        "Heading.TLabel",
        background=cls.BG,
        foreground=cls.TAB_BG,
        font=cls.FONT_HEADING,
    )
    style.configure(
        "Footer.TLabel", background=cls.BG, foreground=cls.TEXT,
        font=cls.FONT_TABLE,
    )

    # Кнопки: прямоугольные, плоские
    style.configure(
        "TButton",
        background=cls.BTN_BG,
        foreground=cls.BTN_FG,
        font=cls.FONT_BUTTON,
        borderwidth=0,
        relief="flat",
        padding=(16, 6),
        bordercolor=cls.BTN_BG,
        lightcolor=cls.BTN_BG,
        darkcolor=cls.BTN_BG,
        focuscolor=cls.BTN_BG,
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("disabled", "#90A4AE"), ("active", cls.TAB_BG)],
        foreground=[("disabled", "#ECEFF1"), ("active", cls.BTN_FG)],
        bordercolor=[("disabled", "#90A4AE"), ("active", cls.TAB_BG)],
        lightcolor=[("disabled", "#90A4AE"), ("active", cls.TAB_BG)],
        darkcolor=[("disabled", "#90A4AE"), ("active", cls.TAB_BG)],
    )

    # Поля ввода
    style.configure(
        "TEntry", fieldbackground="white", foreground=cls.TEXT,
        font=cls.FONT_LABEL, padding=3,
    )
    style.map("TEntry", fieldbackground=[("readonly", "#CFD8DC")])
    style.configure(
        "TCombobox", fieldbackground="white", foreground=cls.TEXT,
        font=cls.FONT_LABEL, padding=3,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "white")],
        selectbackground=[("readonly", "white")],
        selectforeground=[("readonly", cls.TEXT)],
    )
    style.configure(
        "TSpinbox", fieldbackground="white", foreground=cls.TEXT,
        font=cls.FONT_LABEL, padding=3,
    )

    # Вкладки
    style.configure(
        "TNotebook",
        background=cls.TAB_BG,
        borderwidth=0,
        bordercolor=cls.TAB_BG,
        lightcolor=cls.TAB_BG,
        darkcolor=cls.TAB_BG,
        tabmargins=(6, 6, 6, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=cls.TAB_BG,
        foreground=cls.TAB_FG,
        font=cls.FONT_BUTTON,
        padding=(18, 7),
        borderwidth=0,
        bordercolor=cls.TAB_BG,
        lightcolor=cls.TAB_BG,
        darkcolor=cls.TAB_BG,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", cls.BTN_BG), ("active", "#1976D2")],
        foreground=[("selected", cls.TAB_FG), ("active", cls.TAB_FG)],
        bordercolor=[("selected", cls.BTN_BG)],
        lightcolor=[("selected", cls.BTN_BG)],
        darkcolor=[("selected", cls.BTN_BG)],
    )

    # Таблицы: шрифт Tahoma 9
    style.configure(
        "Treeview",
        background="white",
        foreground=cls.TEXT,
        fieldbackground="white",
        font=cls.FONT_TABLE,
        rowheight=26,
        borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", cls.BTN_BG)],
        foreground=[("selected", cls.BTN_FG)],
    )
    style.configure(
        "Treeview.Heading",
        background="#CFD8DC",
        foreground=cls.TAB_BG,
        font=("Tahoma", 10, "bold"),
        relief="flat",
        padding=(6, 6),
    )
    style.map("Treeview.Heading", background=[("active", "#B0BEC5")])
