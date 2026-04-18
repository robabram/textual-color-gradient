#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import colorsys

from textual import on
from textual.app import App, ComposeResult
from textual.color import HSV
from textual.containers import VerticalGroup, Grid
from textual.geometry import clamp
from textual.widget import Widget
from textual.widgets import Static, Header, Footer
from textual_thin_slider import ThinSlider

from src.textual_color_gradient.color_gradient import ColorGradient, GRADIENT_RANGE_MIN, GRADIENT_RANGE_MAX


class ColorSelectHSVControls(Grid):

    def compose(self) -> ComposeResult:
        yield Static("Hue\nSaturation\nValue", id="cs-hsv-labels")
        with VerticalGroup(id="cs-hsv-controls"):
            yield ThinSlider(id='cs-hsv-slider-hue', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX, step=1,
                             name='HUE')
            yield ThinSlider(id='cs-hsv-slider-sat', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX,
                             value=127, step=1, name='SAT')
            yield ThinSlider(id='cs-hsv-slider-val', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX,
                             value=127, step=1, name='VAL')


class ColorSelectRGBControls(Grid):

    def compose(self) -> ComposeResult:
        yield Static("Red   :\nGreen :\nBlue  :", id="cs-rgb-labels")
        with VerticalGroup(id="cs-rgb-controls"):
            yield ThinSlider(id='cs-rgb-slider-red', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX, step=1,
                             name='RED')
            yield ThinSlider(id='cs-rgb-slider-grn', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX, step=1,
                             name='GRN')
            yield ThinSlider(id='cs-rgb-slider-blu', range_min=GRADIENT_RANGE_MIN, range_max=GRADIENT_RANGE_MAX, step=1,
                             name='BLU')


class ColorSelect(Grid):

    cg_widget: ColorGradient = None
    gradient_update: bool = True

    def compose(self) -> ComposeResult:
        if not self.cg_widget:
            self.cg_widget = ColorGradient(id='cs-color-picker-gradient')
        yield self.cg_widget
        yield Static("Color Box", id="cs-color-box")
        # yield Static("RGB Val 1", id="cs-rgb-val-group")
        yield ColorSelectHSVControls()
        yield ColorSelectRGBControls()
        # yield Static("Buttons", id="cs-buttons-group")

    def update_sliders(self, control_id: str | None):

        # Update HSV/RGB sliders
        hsv = self.cg_widget.value
        rgb = colorsys.hsv_to_rgb(*hsv)

        hue = round(hsv.h * GRADIENT_RANGE_MAX)
        hue_pct = round(hsv.h * 100)
        sat = round(hsv.s * GRADIENT_RANGE_MAX)
        sat_pct = round(hsv.s * 100)
        val = round(hsv.v * GRADIENT_RANGE_MAX)
        val_pct = round(hsv.v * 100)

        def set_value(widget: Widget, value):
            """ Prevent event cascade """
            with widget.prevent(ThinSlider.Changed):
                widget.value = value

        if control_id != 'cs-hsv-slider-hue':
            set_value(self.query_exactly_one(f"#cs-hsv-slider-hue"), hue)
        if control_id != 'cs-hsv-slider-sat':
            set_value(self.query_exactly_one(f"#cs-hsv-slider-sat"), sat)
        if control_id != 'cs-hsv-slider-val':
            set_value(self.query_exactly_one(f"#cs-hsv-slider-val"), val)

        red = round(rgb[0] * GRADIENT_RANGE_MAX)
        green = round(rgb[1] * GRADIENT_RANGE_MAX)
        blue = round(rgb[2] * GRADIENT_RANGE_MAX)

        if control_id != 'cs-rgb-slider-red':
            set_value(self.query_exactly_one(f"#cs-rgb-slider-red"), red)
        if control_id != 'cs-rgb-slider-green':
            set_value(self.query_exactly_one(f"#cs-rgb-slider-grn"), green)
        if control_id != 'cs-rgb-slider-blue':
            set_value(self.query_exactly_one(f"#cs-rgb-slider-blu"), blue)

        self.query_exactly_one(f"#cs-hsv-labels").update(f"   Hue : {hue_pct}%\n   Sat : {sat_pct}%\n   Val : {val_pct}%")
        self.query_exactly_one(f"#cs-rgb-labels").update(f"   Red : {red}\n Green : {green}\n  Blue : {blue}")
        cb = self.query_exactly_one(f"#cs-color-box")
        segment = f"[ on rgb({red},{green},{blue})]" + (" " * cb.content_size.width)
        cb.update(f"{segment}\n" * cb.content_size.height)

    def clean_hsv(self, hsv: HSV) -> HSV:
        return HSV(
            clamp(hsv.h, 0.0, 1.0),
            clamp(hsv.s, 0.0, 1.0),
            clamp(hsv.v, 0.0, 1.0)
        )

    @on(ThinSlider.Changed, "#cs-hsv-slider-hue")
    def on_slider_changed_hsv_hue(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = HSV(event.value / GRADIENT_RANGE_MAX, self.cg_widget.value.s, self.cg_widget.value.v)
        self.cg_widget.value = self.clean_hsv(hsv)

    @on(ThinSlider.Changed, "#cs-hsv-slider-sat")
    def on_slider_changed_hsv_sat(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = HSV(self.cg_widget.value.h, event.value / GRADIENT_RANGE_MAX, self.cg_widget.value.v)
        self.cg_widget.value = self.clean_hsv(hsv)

    @on(ThinSlider.Changed, "#cs-hsv-slider-val")
    def on_slider_changed_hsv_val(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = HSV(self.cg_widget.value.h, self.cg_widget.value.s, event.value / GRADIENT_RANGE_MAX)
        self.cg_widget.value = self.clean_hsv(hsv)

    @on(ThinSlider.Changed, "#cs-rgb-slider-red")
    def on_slider_changed_rgb_red(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = colorsys.rgb_to_hsv(
            event.value / GRADIENT_RANGE_MAX,
            self.query_exactly_one(f"#cs-rgb-slider-grn").value / GRADIENT_RANGE_MAX,
            self.query_exactly_one(f"#cs-rgb-slider-blu").value / GRADIENT_RANGE_MAX
        )
        self.cg_widget.value = self.clean_hsv(HSV(*hsv))

    @on(ThinSlider.Changed, "#cs-rgb-slider-grn")
    def on_slider_changed_rgb_grn(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = colorsys.rgb_to_hsv(
            self.query_exactly_one(f"#cs-rgb-slider-red").value / GRADIENT_RANGE_MAX,
            event.value / GRADIENT_RANGE_MAX,
            self.query_exactly_one(f"#cs-rgb-slider-blu").value / GRADIENT_RANGE_MAX
        )
        self.cg_widget.value = self.clean_hsv(HSV(*hsv))

    @on(ThinSlider.Changed, "#cs-rgb-slider-blu")
    def on_slider_changed_rgb_blu(self, event: ThinSlider.Changed) -> None:
        event.stop()
        hsv = colorsys.rgb_to_hsv(
            self.query_exactly_one(f"#cs-rgb-slider-red").value / GRADIENT_RANGE_MAX,
            self.query_exactly_one(f"#cs-rgb-slider-grn").value / GRADIENT_RANGE_MAX,
            event.value / GRADIENT_RANGE_MAX
        )
        self.cg_widget.value = self.clean_hsv(HSV(*hsv))

    @on(ColorGradient.Changed)
    def on_color_picker_gradient_changed(self, event: ColorGradient.Changed) -> None:
        event.stop()
        if self.gradient_update:
            self.update_sliders(None)


class ContentApp(App):
    CSS_PATH = "color_picker.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ColorSelect()


if __name__ == "__main__":
    app = ContentApp()
    app.run()
