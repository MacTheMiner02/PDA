from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309

from PIL import ImageFont

from gpiozero import Button

from button import Buttons

serial = i2c(port=1, address=0x3C)
device = ssd1309(serial, width=128, height=64)

font = ImageFont.truetype("DejaVuSans.ttf", 8)

btn = Buttons()


letterLayout = [
  ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
  ["A", "S", "D", "F", "G", "H", "J", "K", "L", "?"],
  ["Z", "X", "C", "V", "B", "N", "M", ".", ",", "!"],
  ["spce", "back", "caps", "swap"]
]

symbolLayout = [
  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
  ["-", "_", ":", ";", "'", "(", ")", "/", " ", " "],
  [".", ",", "?", "!", "@", "#", "$", "%", "&", "*"],
  ["spce", "back", "caps", "swap"]
]


chosenIndex = (0, 0)
currLayout = letterLayout

caps = True

while True:
  chosenLetter = currLayout[chosenIndex[0]][chosenIndex[1]]

  if caps == False:
    for i in range(len(currLayout)):
      for l in range(len(currLayout[i])):
        currLayout[i][l] = currLayout[i][l].lower()

  # Getting button presses
  for e in btn.pop_events():
    if e == "LEFT":
      # If up is pressed and it's not at the fisrt position then move
      if chosenIndex[1] != 0:
        chosenIndex = (chosenIndex[0], chosenIndex[1]-1)
      # But if it is at the first position then wrap to the last
      else:
        chosenIndex = (chosenIndex[0], 9)
    # Repeat for every other key
    if e == "RIGHT":
      if chosenIndex[1] != 9:
        chosenIndex = (chosenIndex[0], chosenIndex[1]+1)
      else:
        chosenIndex = (chosenIndex[0], 0)
    if e == "UP":
      if chosenIndex[0] != 0:
        chosenIndex = (chosenIndex[0]-1, chosenIndex[1])
      else:
        chosenIndex = (3, chosenIndex[1])
    if e == "DOWN":
      if chosenIndex[0] != 3:
        chosenIndex = (chosenIndex[0]+1, chosenIndex[1])
      # Special case for bottom buttons where it manually sets you to a certain button
      elif chosenIndex[0] == 3:
        if chosenIndex[0] in [0, 1, 2]:
          chosenIndex[0] = 0
        elif chosenIndex[0] in [3, 4]:
          chosenIndex[0] = 1
        elif chosenIndex[0] in [5, 6]:
          chosenIndex[0] = 2
        elif chosenIndex[0] in [7, 8, 9]:
          chosenIndex[0] = 3
      else:
       chosenIndex = (0, chosenIndex[1])
      if e == "OKAY":
        print(chosenLetter)

  # Setting up layout of keyboard
  w, h = 10, 10
  x, y = 10, 23

  # Drawing the keyboard
  with canvas(device) as draw:
    # Looping through the 4 key rows
    for i in range(4):
      # If it is within the three standard rows of the keyboard:
      if i != 3:
        # Loop through each key
        for j in range(10):
          # If the key rendered is the selected key, invert everything
          bgHighlight = 0
          txtColor = 1
          if chosenLetter == currLayout[i][j]:
            bgHighlight = 1
            txtColor = 0
          # Draw the boxes and the text inside them
          draw.rectangle((x+j*w, y+i*h, x+w+j*w, y+h+i*h), outline=1, fill=bgHighlight)
          draw.text((x+j*w + 2, y+i*h), currLayout[i][j], fill=txtColor, font=font)
      else:
        # But if it's the last row then draw 4 boxes that stretch across the scrren
        for j in range(4):
          bgHighligh = 0
          txtColor = 1
          if chosenLetter == currLayout[i][j]:
           bgHighlight = 1
           txtColor = 0
      
          x1 = x + j*25
          x2 = x1 + 25
          y1 = y + i*h
          y2 = y1 + h
          draw.rectangle((x1, y1, x2, y2), outline=1, fill=bgHighlight)
          draw.text((x1+1, y1), currLayout[i][j], fill=txtColor, font=font)
