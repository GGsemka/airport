"""Модальные окна: авторизация, авиакомпании, гейты, рейсы."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from models import DATETIME_FORMAT, FLIGHT_STATUSES
from theme import Theme
from validators import ValidationError, Validator


class BaseDialog(tk.Toplevel):
  """Базовое модальное окно с сеткой «подпись — поле» и кнопками."""

  def __init__(self, parent, title):
    super().__init__(parent, bg=Theme.BG)
    self.parent = parent
    self.title(title)
    self.resizable(False, False)
    self.transient(parent)
    self.result = None

    self.form = ttk.Frame(self, padding=(22, 18))
    self.form.pack(fill="both", expand=True)
    self.form.columnconfigure(1, weight=1)
    self._row = 0

    self.bind("<Escape>", lambda _e: self.destroy())
    self.bind("<Return>", lambda _e: self.on_save())

  def add_field(self, label, widget):
    ttk.Label(self.form, text=label).grid(
        row=self._row, column=0, sticky="w", pady=6
    )
    widget.grid(row=self._row, column=1, sticky="ew", padx=(14, 0), pady=6)
    self._row += 1
    return widget

  def add_entry(self, label, value="", width=32, **kwargs):
    var = tk.StringVar(value=value)
    entry = ttk.Entry(self.form, textvariable=var, width=width, **kwargs)
    self.add_field(label, entry)
    return var, entry

  def add_buttons(self, save_text="Сохранить", cancel_text="Отмена"):
    bar = ttk.Frame(self.form)
    bar.grid(row=self._row, column=0, columnspan=2, sticky="e", pady=(16, 0))
    ttk.Button(bar, text=save_text, command=self.on_save).pack(side="left")
    ttk.Button(bar, text=cancel_text, command=self.destroy).pack(
        side="left", padx=(10, 0)
    )

  def on_save(self):
    raise NotImplementedError

  def error(self, message, title="Ошибка ввода"):
    messagebox.showerror(title, message, parent=self)

  def show(self):
    """Показывает окно модально и возвращает результат (или None)."""
    self.update_idletasks()
    x = self.parent.winfo_rootx() + (
        self.parent.winfo_width() - self.winfo_reqwidth()
    ) // 2
    y = self.parent.winfo_rooty() + (
        self.parent.winfo_height() - self.winfo_reqheight()
    ) // 3
    self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    try:
      self.wait_visibility()
      self.grab_set()
    except tk.TclError:
      pass
    self.focus_set()
    self.wait_window(self)
    return self.result


class LoginDialog(BaseDialog):

  def __init__(self, parent, manager):
    super().__init__(parent, "Авторизация")
    self.manager = manager
    self.result = False

    self.v_login, self.entry_login = self.add_entry("Логин:", width=26)
    self.v_pass, self.entry_pass = self.add_entry(
        "Пароль:", width=26, show="*"
    )
    self.add_buttons(save_text="Войти")
    self.entry_login.focus_set()

  def on_save(self):
    ok, msg = self.manager.authenticate(
        self.v_login.get().strip(), self.v_pass.get()
    )
    if ok:
      self.result = True
      self.destroy()
    else:
      self.error(msg, title="Ошибка")
      self.entry_pass.delete(0, "end")
      self.entry_pass.focus_set()


class AirlineDialog(BaseDialog):

  def __init__(self, parent, airline=None):
    super().__init__(
        parent,
        "Редактирование авиакомпании" if airline else "Новая авиакомпания",
    )
    self.v_name, self.entry_name = self.add_entry(
        "Название:", airline.name if airline else ""
    )
    self.v_iata, _ = self.add_entry(
        "Код IATA:", airline.iata_code if airline else "", width=8
    )
    self.v_country, _ = self.add_entry(
        "Страна:", airline.country if airline else ""
    )
    self.v_phone, _ = self.add_entry(
        "Телефон:", airline.phone if airline else ""
    )
    self.add_buttons()
    self.entry_name.focus_set()

  def on_save(self):
    try:
      data = {
          "name": Validator.required(self.v_name.get(), "Название"),
          "iata_code": Validator.iata(self.v_iata.get()),
          "country": Validator.required(self.v_country.get(), "Страна"),
          "phone": Validator.required(self.v_phone.get(), "Телефон"),
      }
    except ValidationError as e:
      self.error(str(e))
      return
    self.result = data
    self.destroy()


class GateDialog(BaseDialog):

  def __init__(self, parent, gate=None):
    super().__init__(
        parent, "Редактирование гейта" if gate else "Новый гейт"
    )
    self.v_number, self.entry_number = self.add_entry(
        "Номер гейта:", gate.number if gate else "", width=16
    )
    self.v_terminal, _ = self.add_entry(
        "Терминал:", gate.terminal if gate else "", width=16
    )
    self.v_capacity, _ = self.add_entry(
        "Вместимость (пасс.):", str(gate.capacity) if gate else "", width=16
    )
    self.add_buttons()
    self.entry_number.focus_set()

  def on_save(self):
    try:
      data = {
          "number": Validator.required(self.v_number.get(), "Номер гейта"),
          "terminal": Validator.required(self.v_terminal.get(), "Терминал"),
          "capacity": Validator.capacity(self.v_capacity.get()),
      }
    except ValidationError as e:
      self.error(str(e))
      return
    self.result = data
    self.destroy()


class DateTimePicker(ttk.Frame):
  """Выбор даты (день / месяц / год) и времени (часы : минуты)."""

  MONTHS = (
      "января", "февраля", "марта", "апреля", "мая", "июня",
      "июля", "августа", "сентября", "октября", "ноября", "декабря",
  )

  def __init__(self, parent, value=None):
    super().__init__(parent)
    value = value or datetime.now().replace(second=0, microsecond=0)

    self.v_day = tk.StringVar()
    self.v_year = tk.StringVar()
    self.v_hour = tk.StringVar()
    self.v_minute = tk.StringVar()

    self.cb_day = ttk.Combobox(
        self, textvariable=self.v_day, state="readonly", width=3,
        values=[str(d) for d in range(1, 32)],
    )
    self.cb_month = ttk.Combobox(
        self, state="readonly", width=9, values=self.MONTHS
    )
    self.cb_year = ttk.Combobox(
        self, textvariable=self.v_year, state="readonly", width=5
    )
    self.sp_hour = ttk.Spinbox(
        self, textvariable=self.v_hour, from_=0, to=23, wrap=True, width=3,
        format="%02.0f",
    )
    self.sp_minute = ttk.Spinbox(
        self, textvariable=self.v_minute, from_=0, to=59, wrap=True, width=3,
        format="%02.0f",
    )

    self.cb_day.pack(side="left")
    self.cb_month.pack(side="left", padx=(6, 0))
    self.cb_year.pack(side="left", padx=(6, 0))
    ttk.Label(self, text="  ").pack(side="left")
    self.sp_hour.pack(side="left")
    ttk.Label(self, text=":").pack(side="left", padx=2)
    self.sp_minute.pack(side="left")

    self.set(value)

  def set(self, value):
    years = set(range(datetime.now().year - 1, datetime.now().year + 6))
    years.add(value.year)
    self.cb_year.configure(values=[str(y) for y in sorted(years)])
    self.v_day.set(str(value.day))
    self.cb_month.current(value.month - 1)
    self.v_year.set(str(value.year))
    self.v_hour.set(f"{value.hour:02d}")
    self.v_minute.set(f"{value.minute:02d}")

  def get(self):
    try:
      return datetime(
          int(self.v_year.get()),
          self.cb_month.current() + 1,
          int(self.v_day.get()),
          int(self.v_hour.get()),
          int(self.v_minute.get()),
      )
    except ValueError:
      raise ValidationError(
          "Некорректная дата или время вылета (проверьте день месяца, "
          "часы 0–23 и минуты 0–59)"
      ) from None


class FlightDialog(BaseDialog):

  def __init__(self, parent, manager, flight=None):
    super().__init__(
        parent, "Редактирование рейса" if flight else "Новый рейс"
    )
    self.airlines = list(manager.airlines)
    self.gates = list(manager.gates)

    self.cb_airline = ttk.Combobox(
        self.form, state="readonly", width=34,
        values=[str(a) for a in self.airlines],
    )
    self.add_field("Авиакомпания:", self.cb_airline)

    self.cb_gate = ttk.Combobox(
        self.form, state="readonly", width=34,
        values=[str(g) for g in self.gates],
    )
    self.add_field("Гейт:", self.cb_gate)

    self.v_number, self.entry_number = self.add_entry(
        "Номер рейса:", flight.flight_number if flight else ""
    )
    self.v_dest, _ = self.add_entry(
        "Направление:", flight.destination if flight else ""
    )

    start = None
    if flight:
      try:
        start = datetime.strptime(flight.departure_time, DATETIME_FORMAT)
      except ValueError:
        start = None
    self.picker = DateTimePicker(self.form, start)
    self.add_field("Дата и время вылета:", self.picker)

    self.cb_status = ttk.Combobox(
        self.form, state="readonly", width=34, values=FLIGHT_STATUSES
    )
    self.add_field("Статус:", self.cb_status)

    self.v_pax, _ = self.add_entry(
        "Пассажиров:", str(flight.passengers) if flight else "", width=12
    )

    self.v_load = tk.StringVar(value="—")
    self.add_field(
        "Загрузка гейта (%):",
        ttk.Entry(
            self.form, textvariable=self.v_load, state="readonly", width=12
        ),
    )

    if flight:
      if flight.airline in self.airlines:
        self.cb_airline.current(self.airlines.index(flight.airline))
      if flight.gate in self.gates:
        self.cb_gate.current(self.gates.index(flight.gate))
      if flight.status in FLIGHT_STATUSES:
        self.cb_status.current(FLIGHT_STATUSES.index(flight.status))
    else:
      self.cb_status.current(0)

    self.v_pax.trace_add("write", self._update_load)
    self.cb_gate.bind("<<ComboboxSelected>>", self._update_load)
    self._update_load()

    self.add_buttons()
    self.entry_number.focus_set()

  def _update_load(self, *_args):
    """Автоматический расчёт загрузки гейта (только чтение)."""
    index = self.cb_gate.current()
    try:
      gate = self.gates[index] if index >= 0 else None
      pax = int(self.v_pax.get().strip())
      if gate is None or pax < 0:
        raise ValueError
      self.v_load.set(f"{pax / gate.capacity * 100:.1f}")
    except ValueError:
      self.v_load.set("—")

  def on_save(self):
    try:
      if self.cb_airline.current() < 0:
        raise ValidationError("Выберите авиакомпанию")
      if self.cb_gate.current() < 0:
        raise ValidationError("Выберите гейт")
      airline = self.airlines[self.cb_airline.current()]
      gate = self.gates[self.cb_gate.current()]
      flight_number = Validator.required(self.v_number.get(), "Номер рейса")
      destination = Validator.required(self.v_dest.get(), "Направление")
      departure = self.picker.get()
      status = self.cb_status.get()
      if status not in FLIGHT_STATUSES:
        raise ValidationError("Выберите статус")
      passengers = Validator.passengers(self.v_pax.get(), gate.capacity)
    except ValidationError as e:
      self.error(str(e))
      return
    self.result = {
        "airline": airline,
        "flight_number": flight_number,
        "gate": gate,
        "destination": destination,
        "departure_time": departure.strftime(DATETIME_FORMAT),
        "status": status,
        "passengers": passengers,
    }
    self.destroy()
