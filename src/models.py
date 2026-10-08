"""Модели предметной области: авиакомпании, гейты, рейсы."""

DATETIME_FORMAT = "%d.%m.%Y %H:%M"

FLIGHT_STATUSES = (
    "По расписанию",
    "Регистрация",
    "Посадка",
    "Вылетел",
    "Задержан",
    "Отменён",
)


class Airline:

  def __init__(self, id_val, name, iata_code, country, phone):
    self.id = id_val
    self.name = name
    self.iata_code = iata_code
    self.country = country
    self.phone = phone

  def __str__(self):
    return f"{self.name} ({self.iata_code})"


class Gate:

  def __init__(self, id_val, number, terminal, capacity):
    self.id = id_val
    self.number = number
    self.terminal = terminal
    self.capacity = int(capacity)

  def __str__(self):
    return f"{self.number} (терм. {self.terminal})"


class Flight:

  def __init__(
      self,
      id_val,
      airline,
      flight_number,
      gate,
      destination,
      departure_time,
      status,
      passengers,
  ):
    self.id = id_val
    self.airline = airline  # Объект Airline
    self.flight_number = flight_number
    self.gate = gate  # Объект Gate
    self.destination = destination
    self.departure_time = departure_time  # строка в формате DATETIME_FORMAT
    self.status = status
    self.passengers = int(passengers)
