"""Генерирует логотип (160x70) и иконку приложения в папке assets/.

Запуск: python make_assets.py  (нужен Pillow). Файл assets/logo.png можно
заменить любым своим изображением, например созданным нейросетью, — приложение
само приведёт его к размеру 160x70 (если установлен Pillow).
"""

import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SCALE = 4


def gradient(size, top, bottom):
  w, h = size
  img = Image.new("RGB", size)
  px = img.load()
  for y in range(h):
    t = y / max(h - 1, 1)
    color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    for x in range(w):
      px[x, y] = color
  return img


def plane(draw, ox, oy, s):
  """Бумажный самолётик в квадрате s x s с левым верхним углом (ox, oy)."""

  def p(x, y):
    return (ox + x * s, oy + y * s)

  draw.polygon([p(0.05, 0.50), p(0.95, 0.08), p(0.62, 0.92), p(0.46, 0.60)],
               fill=(255, 255, 255))
  draw.polygon([p(0.46, 0.60), p(0.95, 0.08), p(0.50, 0.78)],
               fill=(187, 222, 251))


def font(size, bold=True):
  names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
           "Arial Bold.ttf", "arialbd.ttf", "Tahoma Bold.ttf"]
  for name in names:
    try:
      return ImageFont.truetype(name, size)
    except OSError:
      continue
  return ImageFont.load_default()


def make_logo():
  w, h = 160 * SCALE, 70 * SCALE
  img = gradient((w, h), (13, 71, 161), (25, 118, 210))
  d = ImageDraw.Draw(img)
  plane(d, 12 * SCALE, 11 * SCALE, 48 * SCALE)
  d.text((68 * SCALE, 16 * SCALE), "АЭРОПОРТ", font=font(12 * SCALE),
         fill=(255, 255, 255))
  d.text((69 * SCALE, 38 * SCALE), "учёт рейсов", font=font(11 * SCALE, False),
         fill=(187, 222, 251))
  d.rectangle([69 * SCALE, 56 * SCALE, 150 * SCALE, 57 * SCALE],
              fill=(187, 222, 251))
  return img.resize((160, 70), Image.LANCZOS)


def make_icon():
  size = 256
  img = gradient((size, size), (13, 71, 161), (25, 118, 210))
  d = ImageDraw.Draw(img)
  plane(d, 36, 36, 184)
  return img


if __name__ == "__main__":
  os.makedirs(OUT, exist_ok=True)
  make_logo().save(os.path.join(OUT, "logo.png"))
  icon = make_icon()
  icon.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, "icon.png"))
  icon.save(os.path.join(OUT, "icon.ico"),
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)])
  print("assets готовы:", os.listdir(OUT))
