class ColorDials:
    def __init__(self, red_encoder, green_encoder, blue_encoder, x1_encoder, x2_encoder):
        self._red = red_encoder
        self._green = green_encoder
        self._blue = blue_encoder

        self._x1 = x1_encoder
        self._x2 = x2_encoder

        self.on_change_red = lambda x: None
        self.on_change_green = lambda x: None
        self.on_change_blue = lambda x: None
        self.on_change_x1 = lambda x: None
        self.on_change_x2 = lambda x: None

        red_encoder.on_change = lambda x: self.on_change_red(x)
        green_encoder.on_change = lambda x: self.on_change_green(x)
        blue_encoder.on_change = lambda x: self.on_change_blue(x)
        x1_encoder.on_change = lambda x: self.on_change_x1(x)
        x2_encoder.on_change = lambda x: self.on_change_x2(x)

    def bind(self, color_controller):
        self.on_change_red = lambda x : color_controller.change_red(x)
        self.on_change_green = lambda x : color_controller.change_green(x)
        self.on_change_blue = lambda x : color_controller.change_blue(x)
        #self.on_change_x1 = lambda x : color_controller.change_x1(x)
        #self.on_change_x2 = lambda x : color_controller.change_x2(x)
