#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from textual.app import ComposeResult, App
from textual.color import HSV

from src.textual_color_gradient.color_gradient import ColorGradient


class SimpleGradientApp(App):

    CSS = """
    #simple-gradient {
        width: 40;
        height: 16;
    }
    """

    def compose(self) -> ComposeResult:
        yield ColorGradient(id='simple-gradient', value=HSV(0.65, 0.5, 0.5))


if __name__ == "__main__":
    app = SimpleGradientApp()
    app.run()