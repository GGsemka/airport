import csv
import re
import tkinter as tk
from tkinter import messagebox, ttk


class Airline:

  def __init__(self, id_val, name, iata, country, phone):
    self.id = id_val
    self.name = name
    self.iata = iata
    self.country = country
    self.phone = phone


class Gate:

  def __init__(self, id_val, number, terminal, capacity):
    self.id = id_val
    self.number = number
    self.terminal = terminal
    self.capacity = int(capacity)


class Flight:

  def __init__(
      self,
      id_val,
      airline,
      flight_num,
      gate,
      destination,
      dep_time,
      status,
      passengers,
  ):
    self.id = id_val
    self.airline = airline
    self.gate = gate
    self.flight_num = flight_num
    self.destination = destination
    self.dep_time = dep_time
    self.status = status
    self.passengers = int(passengers)


class AirportApp(tk.Tk):

  def __init__(self):
    super().__init__()

    # ВАЖНО: В заголовке Фамилия и Вариант
    self.title("Иванов В.И. — Вариант 11 | Аэропорт: учет рейсов")
    self.geometry("1100x750")
    self.configure(bg="#ECEFF1")

    # Инициализация хранилищ данных
    self.airlines = []
    self.gates = []
    self.flights = []
    self.is_authenticated = False

    # Настройка стилей
    self._setup_styles()

    # Построение интерфейса (Вкладки, Меню, StatusBar)
    self._build_ui()

  def _setup_styles(self):
    style = ttk.Style()
    style.theme_use("clam")

    # Настройки шрифтов и цветов для таблиц и вкладок
    style.configure(
        "Treeview", font=("Tahoma", 9), rowheight=25, background="#FFFFFF"
    )
    style.configure("Treeview.Heading", font=("Tahoma", 14, "bold"))
    style.configure("TNotebook", background="#0D47A1")
    style.configure(
        "TNotebook.Tab", background="#0D47A1", foreground="#BBDEFB"
    )

  def _build_ui(self):
    # Корневой контейнер вкладок
    self.notebook = ttk.Notebook(self)
    self.notebook.pack(fill="both", expand=True)

    # Создание вкладок
    self.tab_flights = ttk.Frame(self.notebook)
    self.tab_airlines = ttk.Frame(self.notebook)
    self.tab_gates = ttk.Frame(self.notebook)

    self.notebook.add(self.tab_flights, text="Рейсы")  # Активна по умолчанию
    self.notebook.add(self.tab_airlines, text="Авиакомпании")
    self.notebook.add(self.tab_gates, text="Гейты")

    # Панель состояния (StatusBar) внизу
    self.status_bar = tk.Label(
        self,
        text="Статус: Не авторизован",
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.W,
    )
    self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

  # Валидация кода IATA (Пример)
  @staticmethod
  def validate_iata(code):
    return bool(re.match(r"^[A-Z]{2}$", code))


if __name__ == "__main__":
  app = AirportApp()
  app.mainloop()