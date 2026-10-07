"""Вкладки главного окна: таблица, кнопка «Добавить», контекстное меню."""

import sys
import tkinter as tk
from tkinter import messagebox, ttk

from dialogs import AirlineDialog, FlightDialog, GateDialog
from models import Airline, Flight, Gate


class EntityTab(ttk.Frame):
  """Общая вкладка справочника. Наследники задают колонки и действия."""

  title = ""
  entity_type = object
  # (ключ, заголовок, ширина, выравнивание)
  columns = ()

  def __init__(self, parent, app):
    super().__init__(parent)
    self.app = app
    self.manager = app.manager
    self._build()

  # ----- построение интерфейса -----

  def _build(self):
    toolbar = ttk.Frame(self)
    toolbar.pack(fill="x", padx=12, pady=(12, 8))
    ttk.Label(toolbar, text=self.title, style="Heading.TLabel").pack(
        side="left"
    )
    self.btn_add = ttk.Button(toolbar, text="Добавить", command=self.add)
    self.btn_add.pack(side="right")

    self.footer = ttk.Label(self, text="", style="Footer.TLabel")
    self.footer.pack(side="bottom", anchor="w", padx=12, pady=(4, 8))

    box = ttk.Frame(self)
    box.pack(fill="both", expand=True, padx=12)
    box.rowconfigure(0, weight=1)
    box.columnconfigure(0, weight=1)

    self.tree = ttk.Treeview(
        box,
        columns=[c[0] for c in self.columns],
        show="headings",
        selectmode="browse",
    )
    for key, heading, width, anchor in self.columns:
      self.tree.heading(key, text=heading)
      self.tree.column(key, width=width, minwidth=40, anchor=anchor)
    yscroll = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
    xscroll = ttk.Scrollbar(box, orient="horizontal", command=self.tree.xview)
    self.tree.configure(
        yscrollcommand=yscroll.set, xscrollcommand=xscroll.set
    )
    self.tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")

    self.menu = tk.Menu(self, tearoff=0, font=("Tahoma", 10))
    self.menu.add_command(label="Редактировать", command=self.edit)
    self.menu.add_command(label="Удалить", command=self.delete)
    self.menu.add_command(label="Дублировать", command=self.duplicate)

    if sys.platform == "darwin":
      self.tree.bind("<Button-2>", self._on_context)
      self.tree.bind("<Control-Button-1>", self._on_context)
    else:
      self.tree.bind("<Button-3>", self._on_context)

    self.set_authorized(False)

  def _on_context(self, event):
    row = self.tree.identify_row(event.y)
    if not row:
      return
    self.tree.selection_set(row)
    self.tree.focus(row)
    state = "normal" if self.app.is_authorized else "disabled"
    for index in range(3):
      self.menu.entryconfig(index, state=state)
    try:
      self.menu.tk_popup(event.x_root, event.y_root)
    finally:
      self.menu.grab_release()

  def set_authorized(self, authorized):
    self.btn_add.config(state="normal" if authorized else "disabled")

  # ----- данные -----

  def items(self):
    raise NotImplementedError

  def row_values(self, obj):
    raise NotImplementedError

  def selected_object(self):
    selection = self.tree.selection()
    if not selection:
      return None
    obj_id = int(selection[0])
    return next((o for o in self.items() if o.id == obj_id), None)

  def refresh(self, select=None):
    if select is not None and not isinstance(select, self.entity_type):
      select = None
    keep = select.id if select is not None else None
    if keep is None:
      current = self.tree.selection()
      keep = int(current[0]) if current else None

    self.tree.delete(*self.tree.get_children())
    for obj in self.items():
      self.tree.insert("", "end", iid=str(obj.id), values=self.row_values(obj))
    if keep is not None and self.tree.exists(str(keep)):
      self.tree.selection_set(str(keep))
      self.tree.focus(str(keep))
      self.tree.see(str(keep))

  # ----- действия -----

  def add(self):
    raise NotImplementedError

  def edit(self):
    raise NotImplementedError

  def delete(self):
    raise NotImplementedError

  def duplicate(self):
    raise NotImplementedError

  def _confirm_delete(self, text):
    return messagebox.askyesno("Удаление", text, parent=self.app)

  def _warn(self, error, title="Операция невозможна"):
    messagebox.showwarning(title, str(error), parent=self.app)


class AirlinesTab(EntityTab):
  title = "Авиакомпании"
  entity_type = Airline
  columns = (
      ("name", "Название", 260, "w"),
      ("iata", "Код IATA", 100, "center"),
      ("country", "Страна", 220, "w"),
      ("phone", "Телефон", 200, "w"),
  )

  def items(self):
    return self.manager.airlines

  def row_values(self, a):
    return (a.name, a.iata_code, a.country, a.phone)

  def add(self):
    if not self.app.is_authorized:
      return
    data = AirlineDialog(self.app).show()
    if data:
      self.app.refresh_all(self.manager.add_airline(**data))

  def edit(self):
    airline = self.selected_object()
    if airline is None or not self.app.is_authorized:
      return
    data = AirlineDialog(self.app, airline).show()
    if data:
      self.manager.update_airline(airline, **data)
      self.app.refresh_all(airline)

  def delete(self):
    airline = self.selected_object()
    if airline is None or not self.app.is_authorized:
      return
    if not self._confirm_delete(f"Удалить авиакомпанию «{airline.name}»?"):
      return
    try:
      self.manager.delete_airline(airline)
    except ValueError as e:
      self._warn(e, "Удаление невозможно")
      return
    self.app.refresh_all()

  def duplicate(self):
    airline = self.selected_object()
    if airline is None or not self.app.is_authorized:
      return
    self.app.refresh_all(self.manager.duplicate_airline(airline))


class GatesTab(EntityTab):
  title = "Гейты"
  entity_type = Gate
  columns = (
      ("number", "Номер гейта", 200, "w"),
      ("terminal", "Терминал", 200, "center"),
      ("capacity", "Вместимость (пасс.)", 220, "center"),
  )

  def items(self):
    return self.manager.gates

  def row_values(self, g):
    return (g.number, g.terminal, g.capacity)

  def add(self):
    if not self.app.is_authorized:
      return
    data = GateDialog(self.app).show()
    if data:
      self.app.refresh_all(self.manager.add_gate(**data))

  def edit(self):
    gate = self.selected_object()
    if gate is None or not self.app.is_authorized:
      return
    data = GateDialog(self.app, gate).show()
    if not data:
      return
    try:
      self.manager.update_gate(gate, **data)
    except ValueError as e:
      self._warn(e, "Изменение невозможно")
      return
    self.app.refresh_all(gate)

  def delete(self):
    gate = self.selected_object()
    if gate is None or not self.app.is_authorized:
      return
    if not self._confirm_delete(f"Удалить гейт «{gate.number}»?"):
      return
    try:
      self.manager.delete_gate(gate)
    except ValueError as e:
      self._warn(e, "Удаление невозможно")
      return
    self.app.refresh_all()

  def duplicate(self):
    gate = self.selected_object()
    if gate is None or not self.app.is_authorized:
      return
    self.app.refresh_all(self.manager.duplicate_gate(gate))


class FlightsTab(EntityTab):
  title = "Рейсы"
  entity_type = Flight
  columns = (
      ("id", "ID", 45, "center"),
      ("airline", "Авиакомпания", 130, "w"),
      ("number", "Номер рейса", 95, "center"),
      ("gate", "Гейт", 105, "w"),
      ("destination", "Направление", 110, "w"),
      ("time", "Время вылета", 115, "center"),
      ("status", "Статус", 95, "center"),
      ("pax", "Пассажиров", 85, "center"),
      ("load", "Загрузка, %", 90, "center"),
      ("deviation", "Отклонение от среднего", 165, "center"),
  )

  def __init__(self, parent, app):
    self._average = 0.0
    super().__init__(parent, app)

  def items(self):
    return self.manager.flights

  def row_values(self, f):
    load = self.manager.calculate_gate_load(f)
    deviation = load - self._average
    return (
        f.id,
        f.airline.name if f.airline else "",
        f.flight_number,
        str(f.gate) if f.gate else "",
        f.destination,
        f.departure_time,
        f.status,
        f.passengers,
        f"{load:.1f}",
        f"{deviation:+.1f}%" if abs(deviation) >= 0.05 else "0.0%",
    )

  def refresh(self, select=None):
    self._average = self.manager.calculate_average_load()
    super().refresh(select)
    if self.manager.flights:
      self.footer.config(
          text=f"Средняя загрузка гейтов: {self._average:.1f}%"
      )
    else:
      self.footer.config(text="")

  def add(self):
    if not self.app.is_authorized:
      return
    if not self.manager.airlines or not self.manager.gates:
      messagebox.showwarning(
          "Нет данных",
          "Сначала добавьте хотя бы одну авиакомпанию и один гейт\n"
          "на соответствующих вкладках.",
          parent=self.app,
      )
      return
    data = FlightDialog(self.app, self.manager).show()
    if data:
      self.app.refresh_all(self.manager.add_flight(**data))

  def edit(self):
    flight = self.selected_object()
    if flight is None or not self.app.is_authorized:
      return
    data = FlightDialog(self.app, self.manager, flight).show()
    if data:
      self.manager.update_flight(flight, **data)
      self.app.refresh_all(flight)

  def delete(self):
    flight = self.selected_object()
    if flight is None or not self.app.is_authorized:
      return
    if self._confirm_delete(f"Удалить рейс {flight.flight_number}?"):
      self.manager.delete_flight(flight)
      self.app.refresh_all()

  def duplicate(self):
    flight = self.selected_object()
    if flight is None or not self.app.is_authorized:
      return
    self.app.refresh_all(self.manager.duplicate_flight(flight))
