#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from textual.color import HSV
from src.textual_color_gradient.color_gradient import ColorGradientRenderer, GRADIENT_RANGE_MIN, GRADIENT_RANGE_MAX


TEST_HSV = (0.0, 121 / GRADIENT_RANGE_MAX, 131 / GRADIENT_RANGE_MAX)
SMALL_WIDTH = SMALL_HEIGHT = 20


def test_renderer_instantiation():
    """ Test that we can instantiate a ColorGradientRenderer class """
    obj = ColorGradientRenderer()
    assert isinstance(obj, ColorGradientRenderer)
    assert obj.GLYPH == '▀'

    assert GRADIENT_RANGE_MIN == 0
    assert GRADIENT_RANGE_MAX == 255


def test_renderer_simple_output():
    """ Test simple renderer output"""
    obj = ColorGradientRenderer()
    assert isinstance(obj, ColorGradientRenderer)

    line_y = 1
    segments = obj.render_line_segment(HSV(*TEST_HSV), line_y, SMALL_WIDTH, SMALL_HEIGHT)
    assert segments
    assert len(segments) == 20

    # Starting Segment
    assert segments[0].style.color.triplet == (242, 242, 242)
    assert segments[0].style.bgcolor.triplet == (235, 235, 235)
    # Ending Segment
    assert segments[19].style.color.triplet == (242, 11, 11)
    assert segments[19].style.bgcolor.triplet == (235, 11, 11)
