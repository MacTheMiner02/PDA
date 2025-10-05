import time
import datetime

from pathlib import Path

from PIL import Image
from PIL import ImageFont

from gpiozero import Button

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309

serial = i2c(port=1, address=0x3C)
device = ssd1309(serial, width=128, height=64)

BASE = str(Path(__file__).parent) + "/"

imageLocation = BASE+"Sprites/"

musicImg = Image.open(imageLocation+"music.png").convert("1")
notesImg = Image.open(imageLocation+"notes.png").convert("1")
calendarImg = Image.open(imageLocation+"calendar.png").convert("1")
clockImg = Image.open(imageLocation+"clock.png").convert("1")

pressedButtons = []

currentScreen = "home"

def makeButton(gpio, name):
  b = Button(gpio, pull_up=True, bounce_time=0.05)
  b.when_pressed = lambda: pressedButtons.append(name) if name not in pressedButtons else None
  b.when_released = lambda: pressedButtons.remove(name) if name in pressedButtons else None
  return b

upButton = makeButton(5, "up")
downButton = makeButton(6, "down")
leftButton = makeButton(12, "left")
rightButton = makeButton(13, "right")
okayButton = makeButton(16, "okay")
homeButton = makeButton(26, "home")


class Cursor:
  def __init__(self, size, icons, iconIndex):
    self.size = size
    self.icons = icons
    self.iconIndex = iconIndex
    self.currIcon = icons[iconIndex]
    self.blinkClock = 0
    self.blinkOn = True

  def update(self):
    if self.currIcon != self.icons[self.iconIndex]:
     self.blinkClock = 0
     self.blinkOn = True
    self.currIcon = self.icons[self.iconIndex]

    self.x = self.currIcon.x -1
    self.y = self.currIcon.y -1

    self.blinkClock += 1

    if self.blinkOn == True:
     if self.blinkClock == 6:
      self.blinkOn = False
      self.blinkClock = 0
    else:
     if self.blinkClock == 4:
      self.blinkOn = True
      self.blinkClock = 0

  def draw(self):
    if self.blinkOn == True:
      draw.rectangle((self.x, self.y, self.x + self.size[0], self.y + self.size[1]), outline=1, fill=0)


class Icon:
  def __init__(self, coords, icon, size):
    self.x = coords[0]
    self.y = coords[1]
    self.icon = icon
    self.size = size

  def draw(self):
    draw.bitmap((self.x, self.y), self.icon, fill=1)


clockIcon = Icon((24, 10), clockImg, (16, 16))
notesIcon = Icon((44, 10), notesImg, (16, 16))
musicIcon = Icon((64, 10), musicImg, (16, 16))
calendarIcon = Icon((84, 10), calendarImg, (16, 16))

homeIcons = [clockIcon, notesIcon, musicIcon, calendarIcon]

homeCursor = Cursor((17, 17), homeIcons, 0)

while True:
  if "home" in pressedButtons:
    currentScreen = "home"

  if currentScreen == "home":
    homeCursor.update()

    if "left" in pressedButtons:
      if homeCursor.currIcon != homeIcons[0]:
        homeCursor.iconIndex -= 1

    if "right" in pressedButtons:
      if homeCursor.iconIndex != len(homeIcons) -1:
        homeCursor.iconIndex += 1

    if "okay" in pressedButtons:
      if homeCursor.currIcon == clockIcon:
        currentScreen = "clock"
      elif homeCursor.currIcon == notesIcon:
        currentScreen = "notes"
      elif homeCursor.currIcon == musicIcon:
        currentScreen = "music"
      elif homeCursor.currIcon == calendarIcon:
        currentScreen = "calendar"
      print(currentScreen)

    with canvas(device) as draw:
      homeCursor.draw()

      clockIcon.draw()
      notesIcon.draw()
      musicIcon.draw()
      calendarIcon.draw()

  elif currentScreen == "clock":
    font = ImageFont.truetype("DejaVuSans.ttf", 28)

    now = datetime.datetime.now().strftime("%H:%M:%S")
    bbox = draw.textbbox((0, 0), now, font=font)

    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (device.width - w) // 2
    y = (device.height - h) // 2

    with canvas(device) as draw:
      draw.text((x, y), now, font=font, fill=1)
