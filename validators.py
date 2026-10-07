"""Валидация данных (п. 2.9 задания)."""

import re
from datetime import datetime

from models import DATETIME_FORMAT


class ValidationError(ValueError):
  """Ошибка проверки введённых данных (текст пригоден для показа)."""


class Validator:
  CAPACITY_MIN = 50
  CAPACITY_MAX = 500

  _IATA_RE = re.compile(r"[A-Z]{2}")
  _INT_RE = re.compile(r"[-+]?[0-9]+")
  _DATE_FORMATS = (
      DATETIME_FORMAT,
      "%Y-%m-%d %H:%M",
      "%Y-%m-%dT%H:%M",
      "%d.%m.%Y",
      "%Y-%m-%d",
  )

  @staticmethod
  def required(value, field):
    value = (value or "").strip()
    if not value:
      raise ValidationError(f"Поле «{field}» не должно быть пустым")
    return value

  @classmethod
  def integer(cls, value, field):
    text = str(value).strip()
    if not cls._INT_RE.fullmatch(text):
      raise ValidationError(f"Поле «{field}» должно быть целым числом")
    return int(text)

  @classmethod
  def iata(cls, value):
    text = (value or "").strip()
    if not cls._IATA_RE.fullmatch(text):
      raise ValidationError(
          "Поле «Код IATA» должно содержать ровно 2 заглавные латинские буквы"
      )
    return text

  @classmethod
  def capacity(cls, value):
    number = cls.integer(value, "Вместимость")
    if not cls.CAPACITY_MIN <= number <= cls.CAPACITY_MAX:
      raise ValidationError(
          "Поле «Вместимость» — целое число от "
          f"{cls.CAPACITY_MIN} до {cls.CAPACITY_MAX}"
      )
    return number

  @classmethod
  def passengers(cls, value, gate_capacity):
    number = cls.integer(value, "Пассажиров")
    if not 0 <= number <= gate_capacity:
      raise ValidationError(
          f"Поле «Пассажиров» — целое число от 0 до {gate_capacity} "
          "(вместимость гейта)"
      )
    return number

  @classmethod
  def parse_datetime(cls, text):
    """Разбирает дату/время из CSV; возвращает datetime."""
    text = (text or "").strip()
    for fmt in cls._DATE_FORMATS:
      try:
        return datetime.strptime(text, fmt)
      except ValueError:
        continue
    raise ValidationError(f"некорректная дата/время «{text}»")
