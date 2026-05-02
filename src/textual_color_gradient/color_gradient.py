#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import colorsys
from math import ceil
from typing import ClassVar, Any, Type, Union, List

from rich.color import Color as RichColor
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.binding import Binding
from textual.color import HSV, Color
from textual.geometry import clamp
from textual.message import Message
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

GRADIENT_RANGE_MIN = 0
GRADIENT_RANGE_MAX = 255

_MOVE_OFFSET = 1 / GRADIENT_RANGE_MAX
_INITIAL_HSV = (0.0, 121 / GRADIENT_RANGE_MAX, 131 / GRADIENT_RANGE_MAX)


class ColorGradientRenderer:

    GLYPH: ClassVar[str] = '▀'

    @classmethod
    def _hsv_to_rgb(cls, hue: int, sat: int, val: int) -> tuple:
        """
        Convert HSV values in the range of 0-255 to RGB values
        :return: Tuple of RGB values in the range of 0-255
        """
        return tuple(round(i * GRADIENT_RANGE_MAX) for i in colorsys.hsv_to_rgb(
            hue / GRADIENT_RANGE_MAX,
            sat / GRADIENT_RANGE_MAX,
            val / GRADIENT_RANGE_MAX
        ))

    @classmethod
    def _gradient_gen(cls, y: int, hue: int, sat: int, val: int, width: int, height: int, target: bool) -> List[Any]:
        """ Calculate the H, S and V values for each cell of the gradient square """
        horz_step = GRADIENT_RANGE_MAX / width
        vert_step = GRADIENT_RANGE_MAX / height
        val_1 = GRADIENT_RANGE_MAX - ceil(y * vert_step)
        val_2 = GRADIENT_RANGE_MAX - ceil((y + 0.5) * vert_step)
        target_x = clamp(round(sat / horz_step), 0, width - 1)
        target_y = clamp(round((GRADIENT_RANGE_MAX - val) / (vert_step / 2)), 0, (height * 2) - 1)
        # Vary the target point color to contrast the background
        target_clr = tuple([clamp(0 + (target_y * vert_step), 0, 255)] * 3)
        segments = list()
        for x in range(width):
            sat = ceil(x * horz_step)
            # Check foreground/background for target match
            use_target_fgcolor = target and x == target_x and (y * 2) == target_y
            use_target_bgcolor = target and x == target_x and (y * 2) == (target_y - 1)
            fgcolor = target_clr if use_target_fgcolor else cls._hsv_to_rgb(hue, sat, val_1)
            bgcolor = target_clr if use_target_bgcolor else cls._hsv_to_rgb(hue, sat, val_2)

            segments.append(
                Segment(
                    cls.GLYPH,
                    Style(
                        color=RichColor.from_rgb(*fgcolor),
                        bgcolor=RichColor.from_rgb(*bgcolor)
                    )
                )
            )
        return segments

    def render_line_segment(self, hsv: HSV, y: int, width: int, height: int, target: bool = True) -> list[Segment]:
        return self._gradient_gen(
            y,
            round(hsv.h * GRADIENT_RANGE_MAX),
            round(hsv.s * GRADIENT_RANGE_MAX),
            round(hsv.v * GRADIENT_RANGE_MAX),
            width, height,
            target
        )


class ColorGradient(Widget, can_focus=True):
    """
    A Textual color gradient color chooser control widget.
    """
    renderer_cls: ClassVar[Type[ColorGradientRenderer]] = ColorGradientRenderer
    renderer: ColorGradientRenderer

    # Prevent user from selecting text within the widget
    ALLOW_SELECT = False

    BINDINGS = [
        Binding("right", "move_right", "Move Right", show=False),
        Binding("left", "move_left", "Move Left", show=False),
        Binding("up", "move_up", "Move Up", show=False),
        Binding("down", "move_down", "Move Down", show=False),
    ]

    COMPONENT_CLASSES = {"color-picker-gradient--color-picker-gradient"}

    value: reactive[HSV] = reactive(HSV(*_INITIAL_HSV), init=False)

    def watch_value(self) -> None:
        self.post_message(self.Changed(self, self.value))

    def to_color(self) -> Color:
        return Color.from_hsv(self.value)

    class Changed(Message):
        """
        Posted when the value of the gradient changes.
        This message can be handled using an `on_gradient_changed` method.
        """
        def __init__(self, color_manager: "ColorGradient", hsv: HSV) -> None:
            super().__init__()
            self.hsv = hsv
            self.__control__: "ColorGradient" = color_manager

        @property
        def control(self) -> "ColorGradient":
            return self.__control__

    # -- ------------------------------------------------------------

    def __init__(self, value: Union[HSV, None] = None, name: Union[str, None] = None, id: Union[str, None] = None,
                 classes: Union[str, None] = None, disabled: bool = False) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled, markup=False)
        self.value = value if value is not None else HSV(*_INITIAL_HSV)
        self.renderer = ColorGradientRenderer()

    def _on_mount(self, event: events.Mount) -> None:
        pass


    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""
        return Strip(self.renderer.render_line_segment(self.value, y, self.content_size.width,
                                                       self.content_size.height), self.size.width)

    async def action_move_up(self) -> None:
        hsv = HSV(self.value.h, self.value.s, clamp(float(self.value.v) + _MOVE_OFFSET, 0.0, 1.0))
        if hsv != self.value:
            self.value = hsv

    async def action_move_down(self) -> None:
        hsv = HSV(self.value.h, self.value.s, clamp(float(self.value.v) - _MOVE_OFFSET, 0.0, 1.0))
        if hsv != self.value:
            self.value = hsv

    async def action_move_left(self) -> None:
        hsv = HSV(self.value.h, clamp(float(self.value.s) - _MOVE_OFFSET, 0.0, 1.0), self.value.v)
        if hsv != self.value:
            self.value = hsv

    async def action_move_right(self) -> None:
        hsv = HSV(self.value.h, clamp(float(self.value.s) + _MOVE_OFFSET, 0.0, 1.0), self.value.v)
        if hsv != self.value:
            self.value = hsv

    async def _on_mouse_up(self, event: events.MouseUp) -> None:
        event.stop()
        color = self.renderer.render_line_segment(self.value, event.y, self.content_size.width,
                                                       self.content_size.height, False)[event.x].style.color
        self.value = HSV(*colorsys.rgb_to_hsv(
            color.triplet.red / GRADIENT_RANGE_MAX,
            color.triplet.green / GRADIENT_RANGE_MAX,
            color.triplet.blue / GRADIENT_RANGE_MAX
        ))


