from gpiozero import Button

DEFAULT_PINS = {
  "UP": 5, "DOWN": 6, "LEFT": 12, "RIGHT":13, "OKAY":16, "HOME": 26
}

class Buttons:
  def __init__(self, pins: dict = None, bounce: float = 0.05):
    self.pins = pins or DEFAULT_PINS
    self._buttons = {}
    self._events = []
    self.held = set()

    for name, gpio in self.pins.items():
      b = Button(gpio, pull_up=True, bounce_time=bounce)
      b.when_pressed = (lambda n=name: self._on_press(n))
      b.when_released = (lambda n=name: self._on_release(n))
      self._buttons[name] = b

  def _on_press(self, name):
    self.held.add(name)
    self._events.append(name)

  def _on_release(self, name):
    self.held.discard(name)

  def pop_events(self):
    ev, self._events = self._events, []
    return ev

  def is_held(self, name):
    return name in self.held

  def any_held(self, *names):
    return any(n in self.held for n in names)

  def all_held(self, name):
    return all(n in self.held for n in names)
