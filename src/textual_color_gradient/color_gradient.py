#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import colorsys
from math import ceil, floor
from typing import ClassVar, Any

from rich.color import Color
from rich.segment import Segment
from rich.style import Style
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

_CV_RANGE_MIN = 0
_CV_RANGE_MAX = 255



class ColorGradient(Widget, can_focus=True):
    """
    A Textual color gradient color chooser control widget.
    """
    GLYPH: ClassVar[str] = '▀'
    # Prevent user from selecting text within the widget
    ALLOW_SELECT = False

    BINDINGS = [
        Binding("right", "move_right", "Move Right", show=False),
        Binding("left", "move_left", "Move Left", show=False),
        Binding("up", "move_up", "Move Up", show=False),
        Binding("down", "move_down", "Move Down", show=False),
    ]

    # Currently selected RGB values
    red: int = 0
    green: int = 0
    blue: int = 0
    # Currently selected HSV values. Range: 0-255.

    hue: reactive[int] = reactive(0)
    sat: reactive[int] = reactive(127)
    val: reactive[int] = reactive(127)

    box_width: int = 0
    box_height: int = 0

    COMPONENT_CLASSES = {"color-picker-gradient--color-picker-gradient"}

    class Changed(Message):
        """
        Posted when the value of the gradient changes.
        This message can be handled using an `on_gradient_changed` method.
        """
        def __init__(self, color_manager: ColorGradient, red: int, green: int, blue: int, hue: int, sat: int,
                            val: int) -> None:
            super().__init__()
            self.red: int = red
            self.green: int = green
            self.blue: int = blue
            self.hue: int = hue
            self.sat: int = sat
            self.val: int = val
            self.color_gradient: ColorGradient = color_manager

        @property
        def control(self) -> ColorGradient:
            return self.color_gradient

    # -- ------------------------------------------------------------

    def __init__(self, red: int = 128, green: int = 0, blue: int = 0, box_width: int = 59, box_height: int = 14, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.red = red
        self.green = green
        self.blue = blue
        self.box_width = max(20, box_width)
        self.box_height = max(20, box_height)

    @classmethod
    def hsv2rgb(cls, h: float, s: float, v: float) -> tuple:
        return tuple(round(i * _CV_RANGE_MAX) for i in colorsys.hsv_to_rgb(
            (h / _CV_RANGE_MAX),
            (s / _CV_RANGE_MAX),
            (v / _CV_RANGE_MAX))
        )

    @classmethod
    def _gradient_gen(cls, y: int, hue: int, sat: int, val: int, width: int, height: int) -> list[Any]:
        """ Calculate the H, S and V values for each cell of the gradient square """
        horz_step = _CV_RANGE_MAX / width
        vert_step = _CV_RANGE_MAX / height
        val_1 = _CV_RANGE_MAX - ceil(y * vert_step)
        val_2 = _CV_RANGE_MAX - ceil((y + 0.5) * vert_step)

        target_x = max(0, min(width, round(val / horz_step))) - 1
        target_y = max(0, min((2 * height) - 1, floor(sat / (vert_step / 2))))

        segments = list()
        target_clr = (225, 225, 225) if target_y > round(height * 0.75) else (30, 30, 30)

        for x in range(width):
            sat = ceil(x * horz_step)
            # Check foreground/background for target match
            fgcolor = target_clr if x == target_x and (y * 2) == target_y else cls.hsv2rgb(hue, sat, val_1)
            bgcolor = target_clr if x == target_x and (y * 2) == (target_y - 1) else cls.hsv2rgb(hue, sat, val_2)

            segments.append(
                Segment(
                    cls.GLYPH,
                    Style(
                        color=Color.from_rgb(*fgcolor),
                        bgcolor=Color.from_rgb(*bgcolor)
                    )
                )
            )
        return segments

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""
        segments = self._gradient_gen(y, self.hue, self.sat, self.val, self.size.width, self.size.height)
        return Strip(segments, self.size.width)

    def update_hsv(self, hue: int = None, sat: int = None, val: int = None):
        self.hue = hue if hue is not None else self.hue
        self.sat = sat if sat is not None else self.sat
        self.val = val if val is not None else self.val
        self.red, self.green, self.blue = self.hsv2rgb(self.hue, self.sat, self.val)

    def update_rgb(self, red: int = None, green: int = None, blue: int = None):
        self.red = red if red is not None else self.red
        self.green = green if green is not None else self.green
        self.blue = blue if blue is not None else self.blue
        self.hue, self.sat, self.val = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        self.render()

    # TODO: Event messages are causing crashes
    # def watch_hue(self):
    #     self.red, self.green, self.blue = self.hsv2rgb(self.hue, self.sat, self.val)
    #     self.post_message(self.Changed(self, self.red, self.green, self.blue, self.hue, self.sat, self.val))
    #
    # def watch_sat(self):
    #     self.red, self.green, self.blue = self.hsv2rgb(self.hue, self.sat, self.val)
    #     self.post_message(self.Changed(self, self.red, self.green, self.blue, self.hue, self.sat, self.val))
    #
    # def watch_val(self):
    #     self.red, self.green, self.blue = self.hsv2rgb(self.hue, self.sat, self.val)
    #     self.post_message(self.Changed(self, self.red, self.green, self.blue, self.hue, self.sat, self.val))

    def action_move_left(self) -> None:
        self.val = max(0, min(_CV_RANGE_MAX, self.val - 1))

    def action_move_right(self) -> None:
        self.val = max(0, min(_CV_RANGE_MAX, self.val + 1))

    def action_move_up(self) -> None:
        self.sat = max(0, min(_CV_RANGE_MAX, self.sat - 1))

    def action_move_down(self) -> None:
        self.sat = max(0, min(_CV_RANGE_MAX, self.sat + 1))