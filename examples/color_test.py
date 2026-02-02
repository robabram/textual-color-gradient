#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import sys
import timeit
import colorsys
from ast import List
from datetime import datetime
from math import ceil
from time import monotonic
from typing import ClassVar

from rich.console import RenderableType
from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Button, Header, Footer
from textual.containers import HorizontalGroup, VerticalGroup,  Grid

from textual_thin_slider import ThinSlider
from src.textual_color_gradient.color_gradient import ColorGradient

_render_time: int = 0

_CV_RANGE_MIN = 0
_CV_RANGE_MAX = 255


class ColorSelectHSVControls(Grid):

    def compose(self) -> ComposeResult:
        yield Static("Hue\nSaturation\nValue", id="cs-hsv-labels")
        with VerticalGroup(id="cs-hsv-controls"):
            yield ThinSlider(id='cs-hsv-slider-hue', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, step=1, name='HSV')
            yield ThinSlider(id='cs-hsv-slider-sat', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, value=127, step=1, name='SAT')
            yield ThinSlider(id='cs-hsv-slider-val', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, value=127, step=1, name='VAL')


class ColorSelectRGBControls(Grid):

    def compose(self) -> ComposeResult:
        yield Static("Red:\nGreed:\nBlue:", id="cs-hsv-labels")
        with VerticalGroup(id="cs-rgb-controls"):
            yield ThinSlider(id='cs-rgb-slider-red', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, step=1, name='RED')
            yield ThinSlider(id='cs-rgb-slider-grn', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, step=1, name='GRN')
            yield ThinSlider(id='cs-rgb-slider-blu', range_min=_CV_RANGE_MIN, range_max=_CV_RANGE_MAX, step=1, name='BLU')


class ColorSelect(Grid):

    # _cm: _ColorManger = None
    #
    # # TODO: Take RGB values in init method...
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._cm = _ColorManger()
    #
    #     self.color_select_gradient = ColorPickerGradient(color_manager=self._cm, id="cs-gradient")

    def compose(self) -> ComposeResult:
            yield ColorGradient(id='cs-color-picker-gradient')
            yield Static("Color Box", id="cs-color-box")
            yield Static("RGB Val 1", id="cs-rgb-val-group")
            yield ColorSelectHSVControls()
            yield ColorSelectRGBControls()
            yield Static("Buttons", id="cs-buttons-group")

    @on(ThinSlider.Changed, "#cs-hsv-slider-hue")
    def on_slider_changed_hsv_hue(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_hsv(hue=event.value)

    @on(ThinSlider.Changed, "#cs-hsv-slider-sat")
    def on_slider_changed_hsv_sat(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_hsv(sat=event.value)

    @on(ThinSlider.Changed, "#cs-hsv-slider-val")
    def on_slider_changed_hsv_val(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_hsv(val=event.value)

    @on(ThinSlider.Changed, "#cs-rgb-slider-red")
    def on_slider_changed_rgb_red(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_rgb(red=event.value)

    @on(ThinSlider.Changed, "#cs-rgb-slider-green")
    def on_slider_changed_rgb_grn(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_rgb(green=event.value)

    @on(ThinSlider.Changed, "#cs-rgb-slider-blue")
    def on_slider_changed_rgb_blu(self, event: ThinSlider.Changed) -> None:
        cpg: Widget = self.query_exactly_one("#cs-color-picker-gradient")
        cpg.update_rgb(blue=event.value)

    @on(ColorGradient.Changed)
    def on_color_picker_gradient_changed(self, event: ColorGradient.Changed) -> None:

        sys.exit(-1)
        # TODO: Update the slider controls with new values...



class ContentApp(App):
    CSS_PATH = "color_test.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ColorSelect()

if __name__ == "__main__":
    app = ContentApp()
    app.run()
