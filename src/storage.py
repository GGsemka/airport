"""Хранилище данных в памяти, авторизация, расчёты и работа с CSV."""

import csv
import os

from models import FLIGHT_STATUSES, DATETIME_FORMAT, Airline, Flight, Gate
from validators import ValidationError, Validator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.txt")
AUTH_ERROR = "Неправильный логин/пароль"


class ImportReport:
  """Итог загрузки рейсов из CSV."""

  def __init__(self):
    self.loaded = 0
    self.created_airlines = 0
    self.created_gates = 0
    self.errors = []


class AirportManager:

  def __init__(self):
    self.airlines = []
    self.gates = []
    self.flights = []
    self.current_user = None
    self._last_id = {"airline": 0, "gate": 0, "flight": 0}

  def _new_id(self, kind):
    self._last_id[kind] += 1
    return self._last_id[kind]

  # ---------- Авторизация ----------

  @property
  def is_authenticated(self):
    return self.current_user is not None

  def authenticate(self, login, password):
    if not os.path.exists(USERS_FILE):
      return False, "Файл users.txt не найден"
    try:
      with open(USERS_FILE, "r", encoding="utf-8-sig") as f:
        for line in f:
          parts = line.strip().split(";")
          if len(parts) >= 3:
            u_login, u_pass, u_name = parts[0], parts[1], parts[2]
            if u_login == login and u_pass == password:
              self.current_user = u_name
              return True, u_name
    except (OSError, UnicodeDecodeError) as e:
      return False, f"Не удалось прочитать users.txt: {e}"
    return False, AUTH_ERROR

  # ---------- Авиакомпании ----------

  def add_airline(self, name, iata_code, country, phone):
    airline = Airline(self._new_id("airline"), name, iata_code, country, phone)
    self.airlines.append(airline)
    return airline

  def update_airline(self, airline, name, iata_code, country, phone):
    airline.name = name
    airline.iata_code = iata_code
    airline.country = country
    airline.phone = phone

  def flights_of_airline(self, airline):
    return [f for f in self.flights if f.airline is airline]

  def delete_airline(self, airline):
    used = len(self.flights_of_airline(airline))
    if used:
      raise ValueError(
          f"Авиакомпания «{airline.name}» используется в рейсах ({used}).\n"
          "Сначала удалите или измените эти рейсы."
      )
    self.airlines.remove(airline)

  def duplicate_airline(self, airline):
    return self.add_airline(
        f"{airline.name} (копия)",
        airline.iata_code,
        airline.country,
        airline.phone,
    )

  # ---------- Гейты ----------

  def add_gate(self, number, terminal, capacity):
    gate = Gate(self._new_id("gate"), number, terminal, capacity)
    self.gates.append(gate)
    return gate

  def flights_of_gate(self, gate):
    return [f for f in self.flights if f.gate is gate]

  def update_gate(self, gate, number, terminal, capacity):
    for fl in self.flights_of_gate(gate):
      if fl.passengers > capacity:
        raise ValidationError(
            f"Нельзя установить вместимость {capacity}: в рейсе "
            f"{fl.flight_number} уже {fl.passengers} пассажиров"
        )
    gate.number = number
    gate.terminal = terminal
    gate.capacity = int(capacity)

  def delete_gate(self, gate):
    used = len(self.flights_of_gate(gate))
    if used:
      raise ValueError(
          f"Гейт «{gate.number}» используется в рейсах ({used}).\n"
          "Сначала удалите или измените эти рейсы."
      )
    self.gates.remove(gate)

  def duplicate_gate(self, gate):
    return self.add_gate(f"{gate.number} (копия)", gate.terminal, gate.capacity)

  # ---------- Рейсы ----------

  def add_flight(
      self,
      airline,
      flight_number,
      gate,
      destination,
      departure_time,
      status,
      passengers,
  ):
    passengers = Validator.passengers(passengers, gate.capacity)
    flight = Flight(
        self._new_id("flight"),
        airline,
        flight_number,
        gate,
        destination,
        departure_time,
        status,
        passengers,
    )
    self.flights.append(flight)
    return flight

  def update_flight(
      self,
      flight,
      airline,
      flight_number,
      gate,
      destination,
      departure_time,
      status,
      passengers,
  ):
    passengers = Validator.passengers(passengers, gate.capacity)
    flight.airline = airline
    flight.flight_number = flight_number
    flight.gate = gate
    flight.destination = destination
    flight.departure_time = departure_time
    flight.status = status
    flight.passengers = passengers

  def delete_flight(self, flight):
    self.flights.remove(flight)

  def duplicate_flight(self, flight):
    return self.add_flight(
        flight.airline,
        flight.flight_number,
        flight.gate,
        flight.destination,
        flight.departure_time,
        flight.status,
        flight.passengers,
    )

  # ---------- Расчёты (п. 2.8) ----------

  def calculate_gate_load(self, flight):
    if not flight.gate or flight.gate.capacity == 0:
      return 0.0
    return (flight.passengers / flight.gate.capacity) * 100.0

  def calculate_average_load(self):
    if not self.flights:
      return 0.0
    loads = [self.calculate_gate_load(f) for f in self.flights]
    return sum(loads) / len(loads)

  def get_deviation(self, flight):
    return self.calculate_gate_load(flight) - self.calculate_average_load()

  # ---------- CSV (п. 2.7) ----------

  def save_to_csv(self, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
      writer = csv.writer(f, delimiter=";")
      for fl in self.flights:
        writer.writerow([
            fl.id,
            fl.airline.id if fl.airline else "",
            fl.airline.name if fl.airline else "",
            fl.airline.iata_code if fl.airline else "",
            fl.gate.id if fl.gate else "",
            fl.gate.number if fl.gate else "",
            fl.gate.terminal if fl.gate else "",
            fl.flight_number,
            fl.destination,
            fl.departure_time,
            fl.status,
            fl.passengers,
        ])

  def _find_airline(self, iata, name):
    same = [a for a in self.airlines if a.iata_code == iata]
    for airline in same:
      if airline.name == name:
        return airline
    return same[0] if same else None

  def _find_gate(self, number, terminal):
    for gate in self.gates:
      if gate.number == number and gate.terminal == terminal:
        return gate
    return None

  @staticmethod
  def _parse_row(row):
    if len(row) != 12:
      raise ValidationError(f"ожидается 12 полей, получено {len(row)}")
    (id_s, _air_id, air_name, iata, _gate_id, gate_number, terminal,
     flight_number, destination, time_s, status, pax_s) = [
         c.strip() for c in row
     ]
    status = Validator.required(status, "Статус")
    if status not in FLIGHT_STATUSES:
      raise ValidationError(f"неизвестный статус «{status}»")
    passengers = Validator.integer(pax_s, "Пассажиров")
    if passengers < 0:
      raise ValidationError("число пассажиров не может быть отрицательным")
    return {
        "id": int(id_s) if id_s.isdigit() else None,
        "airline_name": Validator.required(air_name, "Название"),
        "iata": Validator.iata(iata),
        "gate_number": Validator.required(gate_number, "Номер гейта"),
        "terminal": Validator.required(terminal, "Терминал"),
        "flight_number": Validator.required(flight_number, "Номер рейса"),
        "destination": Validator.required(destination, "Направление"),
        "departure_time": Validator.parse_datetime(time_s).strftime(
            DATETIME_FORMAT
        ),
        "status": status,
        "passengers": passengers,
    }

  def load_from_csv(self, filename):
    """Заменяет рейсы данными из CSV. Некорректные строки пропускаются.

    Авиакомпании и гейты ищутся среди имеющихся (авиакомпания — по коду IATA,
    гейт — по номеру и терминалу); если их нет, создаются. В CSV нет
    вместимости гейта, поэтому у нового гейта она подбирается по числу
    пассажиров (в пределах 50..500).
    """
    report = ImportReport()
    parsed = []
    with open(filename, "r", newline="", encoding="utf-8-sig") as f:
      for line_no, row in enumerate(csv.reader(f, delimiter=";"), start=1):
        if not row or all(not c.strip() for c in row):
          continue
        if line_no == 1 and not row[0].strip().isdigit():
          continue  # строка заголовка
        try:
          parsed.append((line_no, self._parse_row(row)))
        except ValidationError as e:
          report.errors.append(f"Строка {line_no}: {e}")

    # Недостающие гейты создаём один раз, с запасом под все их рейсы
    needed = {}
    for _, r in parsed:
      key = (r["gate_number"], r["terminal"])
      if self._find_gate(*key) is None:
        needed[key] = max(needed.get(key, 0), r["passengers"])
    for (number, terminal), pax in needed.items():
      capacity = min(
          Validator.CAPACITY_MAX, max(Validator.CAPACITY_MIN, pax)
      )
      self.add_gate(number, terminal, capacity)
      report.created_gates += 1

    new_flights = []
    seen_ids = set()
    for line_no, r in parsed:
      gate = self._find_gate(r["gate_number"], r["terminal"])
      if r["passengers"] > gate.capacity:
        report.errors.append(
            f"Строка {line_no}: пассажиров ({r['passengers']}) больше "
            f"вместимости гейта {gate.number} ({gate.capacity})"
        )
        continue
      airline = self._find_airline(r["iata"], r["airline_name"])
      if airline is None:
        airline = self.add_airline(r["airline_name"], r["iata"], "", "")
        report.created_airlines += 1
      flight_id = r["id"]
      if flight_id in seen_ids:
        flight_id = None
      if flight_id is not None:
        seen_ids.add(flight_id)
      new_flights.append(
          Flight(
              flight_id,
              airline,
              r["flight_number"],
              gate,
              r["destination"],
              r["departure_time"],
              r["status"],
              r["passengers"],
          )
      )

    if new_flights or not report.errors:
      last = max(seen_ids, default=0)
      for fl in new_flights:
        if fl.id is None:
          last += 1
          fl.id = last
      self.flights = new_flights
      self._last_id["flight"] = last
      report.loaded = len(new_flights)
    return report
