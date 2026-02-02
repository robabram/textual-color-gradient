#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import colorsys
from math import ceil
from typing import ClassVar, Type, List

from rich.color import Color
from rich.console import RenderableType, ConsoleOptions, RenderResult, Console
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget


_CV_RANGE_MIN = 0
_CV_RANGE_MAX = 255

_RICH_COLOR_WIDTH = 24  # Each character needs this many bytes to represent a Rich color values (Foreground+Background)
_RICH_FORE_OFFSET = 2  # Foreground color offset from _RICH_COLOR_WIDTH position
_RICH_BACK_OFFSET = 14  # Background color offset from _RICH_COLOR_WIDTH position


class GradientColor(Color):
    # TODO: Make the Color class updatable so we don't have to keep instantiating new instances
    ...


class ColorGradientRender:

    GLYPH: ClassVar[str] = '▀'
    __gradient_arr__: bytearray = None

    hue: int = 0
    saturation: int = 0
    value: int = 0

    def __init__(self, hue: int = 0, saturation: int = 100, value: int = 0) -> None:
        self.hue = hue
        self.saturation = saturation
        self.value = value
        # Prebuild an integer to hex string lookup array to help performance
        self._hex_map = [bytearray(hex(i).upper()[2:].zfill(2), 'ascii') for i in range(256)]

    def update(self, hue: int = None, saturation: int = None, value: int = None):
        """ Update the color gradient values and return self """
        self.hue = hue or self.hue
        self.saturation = saturation or self.saturation
        self.value = value or self.value
        return self

    @staticmethod
    def to_hex(red: int | float, green: int | float, blue: int | float) -> str:
        """ Return a Hex Color representation """
        return f"#{int(red):02X}{int(green):02X}{int(blue):02X}"

    @staticmethod
    def hsv2rgb(h: float, s: float, v: float) -> tuple:
        return tuple(round(i * _CV_RANGE_MAX) for i in colorsys.hsv_to_rgb(
            (h / _CV_RANGE_MAX),
            (s / _CV_RANGE_MAX),
            (v / _CV_RANGE_MAX)))

    @staticmethod
    def _gradient_gen(hue: int, width: int, height: int):
        """ Calculate the H, S and V values for each cell of the gradient square """
        h_step = _CV_RANGE_MAX / height
        v_step = _CV_RANGE_MAX / width
        for y in range(height):
            sat_1 = ceil(y * h_step)
            sat_2 = ceil((y + 0.5) * h_step)
            for x in range(width):
                val = ceil(x * v_step)
                # char_off = arr_pos + self._fore_offset
                yield hue, sat_1, sat_2, val, x, y

    def _prerender_bytearray(self, width: int, height: int) -> bytearray:
        """ Return a Gradient Color byte array representation """

        # TODO: Switch to using the GradientColor class for each element...
        arr_pos: int = 0
        gradient_elements = [''] * ((width + 1) * height)

        for hue, sat_1, sat_2, val, x, y in self._gradient_gen(self.hue, width, height):
            gradient_elements[arr_pos] = ''.join([
                f'[{self.to_hex(*self.hsv2rgb(self.hue, sat_1, val))}]',
                f'[on {self.to_hex(*self.hsv2rgb(self.hue, sat_2, val))}]',
                self.GLYPH
            ])
            arr_pos += 1

        return bytearray(''.join(gradient_elements), 'utf-8')

    @classmethod
    def render_gradient(cls, hue: int, saturation: int, value: int, width: int, height: int, hex_map: List,
                        gradient_arr: bytearray) -> str:
        """
        Draw the color gradient
        :param hue: The 'hue' value
        :param saturation: The 'saturation' value
        :param value: The color value
        :param width: The width of the gradient area
        :param height: The height of the gradient area
        :param hex_map: Predefined array of hex values
        :return:
        """
        # style = self.get_component_rich_style("color-picker-gradient--color-picker-gradient")
        arr_pos: int = 0

        # target_x = round(value / (_CV_RANGE_MAX / self.box_width))
        target_x = max(0, min(width - 1, round(value / (_CV_RANGE_MAX / width))))
        # target_y = ceil(self.sat / (_CV_RANGE_MAX / (height * 2)))
        target_y = max(0, min(2 * height - 1, round(saturation / (_CV_RANGE_MAX / ((height * 2) - 1)))))

        for hue, sat_1, sat_2, val, x, y in cls._gradient_gen(hue, width, height):
            char_off = arr_pos + _RICH_FORE_OFFSET
            # Check foreground for target match
            r, g, b = cls.hsv2rgb(hue, sat_1, val)
            if x == target_x:
                if (y * 2) == (target_y):
                    r = g = b = 0

            for i in [r, g, b]:
                gradient_arr[char_off:char_off + 2] = hex_map[i]
                char_off += 2

            char_off = arr_pos + _RICH_BACK_OFFSET
            # Check background for target match
            r, g, b = cls.hsv2rgb(hue, sat_2, val)
            if x == target_x:
                if (y * 2) == (target_y - 1):
                    r = g = b = 0

            for i in [r, g, b]:
                gradient_arr[char_off:char_off + 2] = hex_map[i]
                char_off += 2
            arr_pos += _RICH_COLOR_WIDTH

        # for y in range(int(height)):
        #     sat_1 = float(y) / height
        #     # TODO: Pre-calculate the value to be added to sat_1
        #     sat_2 = (float(y) + self._sat_value_offset) / height
        #     for x in range(int(width)):
        #         val = x / float(width)
        #         char_off = arr_pos + _RICH_FORE_OFFSET
        #         for i in self.hsv2rgb(hue, sat_1, val):
        #             gradient_arr[char_off:char_off+2] = self._hex_map[i]
        #             char_off += 2
        #         char_off = arr_pos + self._back_offset
        #         for i in self.hsv2rgb(hue, sat_2, val):
        #             gradient_arr[char_off:char_off+2] = self._hex_map[i]
        #             char_off += 2
        #         arr_pos += self._char_width

        return gradient_arr.decode('utf-8')

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        width = options.max_width or console.width
        height = options.max_height or console.height

        if not self.__gradient_arr__:
            self.__gradient_arr__ = self._prerender_bytearray(width, height)

        bar = self.render_gradient(
            hue=self.hue,
            saturation=self.saturation,
            value=self.value,
            width=width,
            height=height,
            hex_map=self._hex_map,
            gradient_arr=self.__gradient_arr__
        )
        yield bar


class ColorGradient(Widget, can_focus=True):
    """
    A Textual thin slider control widget.
    """
    renderer_cls: ClassVar[Type[ColorGradientRender]] = ColorGradientRender
    renderer: ColorGradientRender = None

    # Prevent user from selecting text within the widget
    ALLOW_SELECT = False

    BINDINGS = [
        Binding("right", "slide_right", "Slide Right", show=False),
        Binding("left", "slide_left", "Slide Left", show=False),
    ]
    """
    Manage color selection for all widgets.
    """
   # SLIDER_GLYPH = '▀'

    # Currently selected RGB values
    red: int = 0
    green: int = 0
    blue: int = 0
    # Currently selected HSV values. Range: 0-255.

    hue: int = reactive(0)
    sat: int = reactive(127)
    val: int = reactive(127)

    box_width: int = 0
    box_height: int = 0

    gradient_bytearray: bytearray = None
    _hex_map = List = None  # Pre-populated list of 1-byte hex values for quick lookup
    _char_width = 24  # Each color gradient character requires this many bytes in byte-array
    _fore_offset = 2  # Foreground color offset from _char_width position
    _back_offset = 14  # Background color offset from _char_width position

    COMPONENT_CLASSES = {"color-picker-gradient--color-picker-gradient"}
    # BINDINGS = [
    #     Binding("right", "move_right", "Move Right", show=False),
    #     Binding("left", "move_left", "Move Left", show=False),
    #     Binding("up", "move_up", "Move Up", show=False),
    #     Binding("down", "move_down", "Move Down", show=False),
    # ]

    # timer = 0
    # start_time = reactive(monotonic)
    # time = reactive(0.0)
    # total = reactive(0.0)
    #
    # def on_mount(self) -> None:
    #     """ Event handler called when widget is added to the app """
    #     self.update_timer = self.set_interval(1 / 180, self.update_time, pause=False)
    #
    # def update_time(self) -> None:
    #     """Method to update time to current."""
    #     self.time = self.total + (monotonic() - self.start_time)
    #
    # def watch_time(self, time: float) -> None:
    #     """Called when the time attribute changes."""
    #     hue = self.hue + 0.025
    #     if hue > 1.0:
    #         hue = 0.0
    #     self.hue = hue
    #     self.refresh()

    class Changed(Message):
        """Posted when the value of the slider changes.

        This message can be handled using an `on_slider_changed` method.
        """

        def __init__(self, color_manager: ColorGradient, value: int) -> None:
            super().__init__()
            self.value: int = value
            self.color_gradient: ColorGradient = color_manager

        @property
        def control(self) -> ColorGradient:
            return self.color_gradient

    def __init__(self, red: int = 128, green: int = 0, blue: int = 0, box_width: int = 59, box_height: int = 14, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.red = red
        self.green = green
        self.blue = blue
        self.box_width = max(5, box_width)
        self.box_height = max(5, box_height)

        self.renderer = self.renderer_cls(
            hue=self.hue,
            saturation=self.sat,
            value=self.val
        )

        # Prebuild an integer to hex string lookup array to help performance
        # self._hex_map = [bytearray(hex(i).upper()[2:].zfill(2), 'ascii') for i in range(256)]
        # self.gradient_bytearray = self._prerender_bytearray()

    @staticmethod
    def _gradient_gen(hue: int, width: int, height: int):
        """ Calculate the H, S and V values for each cell of the gradient square """
        h_step = _CV_RANGE_MAX / height
        v_step = _CV_RANGE_MAX / width
        for y in range(height):
            sat_1 = ceil(y * h_step)
            sat_2 = ceil((y + 0.5) * h_step)
            for x in range(width):
                val = ceil(x * v_step)
                # char_off = arr_pos + self._fore_offset
                yield hue, sat_1, sat_2, val, x, y

    def render(self) -> RenderableType:
        """ Render the color gradient box """
        return self.renderer.update(self.hue, self.sat, self.val)

    # def render(self) -> RenderableType:
    #     # style = self.get_component_rich_style("color-picker-gradient--color-picker-gradient")
    #     arr_pos: int = 0
    #
    #     # target_x = round(self.val / (_CV_RANGE_MAX / self.box_width))
    #     target_x = max(0, min(self.box_width - 1, round(self.val / (_CV_RANGE_MAX / self.box_width))))
    #
    #     # target_y = ceil(self.sat / (_CV_RANGE_MAX / (self.box_height * 2)))
    #     target_y = max(0, min(2 * self.box_height - 1, round(self.sat / (_CV_RANGE_MAX / ((self.box_height * 2) - 1)))))
    #
    #     for hue, sat_1, sat_2, val, x, y in self._gradient_gen(self.hue, self.box_width, self.box_height):
    #         char_off = arr_pos + self._fore_offset
    #         # Check foreground for target match
    #         r, g, b = self.hsv2rgb(self.hue, sat_1, val)
    #         if x == target_x:
    #             if (y * 2) == (target_y):
    #                 r = g = b = 0
    #
    #         for i in [r, g, b]:
    #             self.gradient_bytearray[char_off:char_off + 2] = self._hex_map[i]
    #             char_off += 2
    #
    #         char_off = arr_pos + self._back_offset
    #         # Check background for target match
    #         r, g, b = self.hsv2rgb(self.hue, sat_2, val)
    #         if x == target_x:
    #             if (y * 2) == (target_y - 1):
    #                 r = g = b = 0
    #
    #         for i in [r, g, b]:
    #             self.gradient_bytearray[char_off:char_off + 2] = self._hex_map[i]
    #             char_off += 2
    #         arr_pos += self._char_width
    #
    #
    #     # for y in range(int(self.box_height)):
    #     #     sat_1 = float(y) / self.box_height
    #     #     # TODO: Pre-calculate the value to be added to sat_1
    #     #     sat_2 = (float(y) + self._sat_value_offset) / self.box_height
    #     #     for x in range(int(self.box_width)):
    #     #         val = x / float(self.box_width)
    #     #         char_off = arr_pos + self._fore_offset
    #     #         for i in self.hsv2rgb(self.hue, sat_1, val):
    #     #             self.gradient_bytearray[char_off:char_off+2] = self._hex_map[i]
    #     #             char_off += 2
    #     #         char_off = arr_pos + self._back_offset
    #     #         for i in self.hsv2rgb(self.hue, sat_2, val):
    #     #             self.gradient_bytearray[char_off:char_off+2] = self._hex_map[i]
    #     #             char_off += 2
    #     #         arr_pos += self._char_width
    #
    #     return self.gradient_bytearray.decode('utf-8')

    def update_hsv(self, hue: int = None, sat: int = None, val: int = None):
        self.hue = hue or self.hue
        self.sat = sat or self.sat
        self.val = val or self.val
        self.red, self.green, self.blue = self.hsv2rgb(self.hue, self.sat, self.val)

    def update_rgb(self, red: int = None, green: int = None, blue: int = None):
        self.red = red or self.red
        self.green = green or self.green
        self.blue = blue or self.blue
        self.hue, self.sat, self.val = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        self.render()

    # @staticmethod
    # def to_hex(red: int | float, green: int | float, blue: int | float) -> str:
    #     """ Return a Hex Color representation """
    #     return f"#{int(red):02X}{int(green):02X}{int(blue):02X}"

    @staticmethod
    def hsv2rgb(h: float, s: float, v: float) -> tuple:
        return tuple(round(i * _CV_RANGE_MAX) for i in colorsys.hsv_to_rgb(
            (h / _CV_RANGE_MAX),
            (s / _CV_RANGE_MAX),
            (v / _CV_RANGE_MAX)))

    @staticmethod
    def rgb_to_hex_to_bytearray(r, g, b) -> bytearray:
        # Shift R 16 bits left, G 8 bits left, and combine with B using OR
        # i_ = (r << 16) | (g << 8) | b
        # h_ = hex(i_)
        # ba_ = bytearray(hex(b), 'ascii')[2:]
        return bytearray(hex((r << 16) | (g << 8) | b), 'ascii')[2:]

    # def to_gradient(self) -> str:
    #     """ Return a Gradient Color representation """
    #     arr_pos: int = 0
    #     for y in range(int(self.box_height)):
    #         sat_1 = y / self.box_height
    #         sat_2 = (y + 0.005) / self.box_height
    #         for x in range(int(self.box_width)):
    #             arr_pos += 1
    #             val = x / float(self.box_width)
    #             self.gradient_elements[arr_pos] = ''.join([
    #                 f'[{self.to_hex(*self.hsv2rgb(self.hue, sat_1, val))}]',
    #                 f'[on {self.to_hex(*self.hsv2rgb(self.hue, sat_2, val))}]'
    #                 '▀'
    #             ])
    #
    #     return ''.join(self.gradient_elements)

    def to_gradient(self) -> str:
        """ Return a Hex Color representation in Rich markdown """
        # TODO: Loop through individual gradient characters and update self.gradient_bytearray
        #       IE: self.gradient_bytearray[2:8] = rgb_to_hex_to_bytearray(RGB)
        pass

    # def _prerender_bytearray(self) -> bytearray:
    #     """ Return a Gradient Color byte array representation """
    #     arr_pos: int = 0
    #     gradient_elements = [''] * ((self.box_width + 1) * self.box_height)
    #
    #     for hue, sat_1, sat_2, val, x, y in self._gradient_gen(self.hue, self.box_width, self.box_height):
    #         gradient_elements[arr_pos] = ''.join([
    #             f'[{self.to_hex(*self.hsv2rgb(self.hue, sat_1, val))}]',
    #             f'[on {self.to_hex(*self.hsv2rgb(self.hue, sat_2, val))}]',
    #             self.SLIDER_GLYPH
    #         ])
    #         arr_pos += 1
    #
    #     return bytearray(''.join(gradient_elements), 'utf-8')
