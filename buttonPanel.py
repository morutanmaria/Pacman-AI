from buttons import Button
class ButtonPanel:
    
    def __init__(self, x, y, button_width, button_height, spacing, font):
        self.buttons = []
        self.x = x
        self.y = y
        self.button_width = button_width
        self.button_height = button_height
        self.spacing = spacing
        self.font = font

    def add_button(self, text, callback):
        index = len(self.buttons)
        bx = self.x
        by = self.y + index * (self.button_height + self.spacing)
        btn = Button(bx, by, self.button_width, self.button_height, text, self.font, callback)
        self.buttons.append(btn)

    def draw(self, surface):
        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)