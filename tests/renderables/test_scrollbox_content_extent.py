"""Port of upstream ScrollBox content-extent tests.

Upstream: packages/core/src/tests/scrollbox-content-extent.test.ts
          (logunovFGP/opentui @ 2837b796)
Tests ported: 3/3 (0 skipped)

`scroll_height` used to be read straight off the content node's own layout
height, so any content whose subtree overflowed that height left the extra rows
unreachable: `max_scroll_y` stopped short of them and `sticky_start="bottom"`
pinned above the real bottom. A container with an explicit height that its
children overflow reproduces that shape directly.
"""

from opentui import create_test_renderer
from opentui.components.box import Box
from opentui.components.scrollbox import ScrollBox
from opentui.components.text import Text


def _rows(count: int) -> list[Text]:
    return [Text(content=f"row {i}", flex_shrink=0) for i in range(count)]


class TestScrollBoxContentExtent:
    """Maps to describe("ScrollBox content extent")."""

    async def test_scroll_height_covers_children_that_overflow_their_container(self):
        """Maps to test("scrollHeight covers children that overflow their container's height")."""
        setup = await create_test_renderer(40, 10)
        try:
            scroll = ScrollBox(id="scroll", width=40, height=10, scroll_y=True)
            setup.renderer.root.add(scroll)

            # The column claims 20 rows; its 50 non-shrinking children need 50.
            column = Box(id="column", flex_direction="column", height=20)
            scroll.add(column)
            for row in _rows(50):
                column.add(row)

            setup.render_frame()
            setup.render_frame()

            assert column._layout_height == 20
            assert scroll.scroll_height == 50

            scroll.scroll_top = 10**9
            assert scroll.scroll_top == 40  # 50 rows of content in a 10-row viewport
        finally:
            setup.destroy()

    async def test_a_sound_layout_is_unaffected(self):
        """Maps to test("a sound layout is unaffected: extent equals the content height")."""
        setup = await create_test_renderer(40, 10)
        try:
            scroll = ScrollBox(id="scroll", width=40, height=10, scroll_y=True)
            setup.renderer.root.add(scroll)

            column = Box(id="column", flex_direction="column")
            scroll.add(column)
            for row in _rows(30):
                column.add(row)

            setup.render_frame()
            setup.render_frame()

            assert scroll.content._layout_height == 30
            assert scroll.scroll_height == 30
        finally:
            setup.destroy()

    async def test_subtree_extent_reaches_through_nested_containers(self):
        """Maps to test("getSubtreeExtentY reaches through nested containers")."""
        setup = await create_test_renderer(40, 10)
        try:
            outer = Box(id="outer", flex_direction="column", height=5)
            setup.renderer.root.add(outer)
            inner = Box(id="inner", flex_direction="column", height=5)
            outer.add(inner)
            for row in _rows(12):
                inner.add(row)

            setup.render_frame()
            setup.render_frame()

            assert outer._layout_height == 5
            assert outer.subtree_extent_y() == 12
        finally:
            setup.destroy()
