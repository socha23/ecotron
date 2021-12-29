class ColorDials:
    def __init__(self, red_encoder, green_encoder, blue_encoder, x_encoder, y_encoder):
        self._red = red_encoder
        self._green = green_encoder
        self._blue = blue_encoder

        self._x = x_encoder
        self._y = y_encoder

        self.on_change_red = lambda x: None
        self.on_change_green = lambda x: None
        self.on_change_blue = lambda x: None
        self.on_change_x = lambda x: None
        self.on_change_y = lambda y: None

        red_encoder.on_change = lambda x: self.on_change_red(x)
        green_encoder.on_change = lambda x: self.on_change_green(x)
        blue_encoder.on_change = lambda x: self.on_change_blue(x)
        x_encoder.on_change = lambda x: self.on_change_x(x)
        y_encoder.on_change = lambda y: self.on_change_y(y)

    def bind(self, controller):
        self.on_change_red = lambda x : controller.change_red(x)
        self.on_change_green = lambda x : controller.change_green(x)
        self.on_change_blue = lambda x : controller.change_blue(x)
        self.on_change_x = lambda x : controller.change_x(x)
        self.on_change_y = lambda y : controller.change_y(y)
