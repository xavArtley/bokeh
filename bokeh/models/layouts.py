#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2019, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------
''' Various kinds of layout components.

'''

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports

# External imports

# Bokeh imports
from ..core.enums import SizingMode, SizingPolicy, Location, TrackAlign
from ..core.has_props import abstract
from ..core.properties import (Bool, Auto, Enum, Int, NonNegativeInt, Float,
    Instance, List, Seq, Tuple, Dict, String, Either, Struct, Color)
from ..core.validation import warning, error
from ..core.validation.warnings import (BOTH_CHILD_AND_ROOT, EMPTY_LAYOUT,
    FIXED_SIZING_MODE, FIXED_WIDTH_POLICY, FIXED_HEIGHT_POLICY)
from ..core.validation.errors import MIN_PREFERRED_MAX_WIDTH, MIN_PREFERRED_MAX_HEIGHT
from ..model import Model
from .callbacks import Callback

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

__all__ = (
    'Box',
    'Column',
    'GridBox',
    'HTMLBox',
    'LayoutDOM',
    'Row',
    'Spacer',
    'WidgetBox',
)

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

@abstract
class LayoutDOM(Model):
    """ The base class for layoutable components.

    """

    disabled = Bool(False, help="""
    Whether the widget will be disabled when rendered.

    If ``True``, the widget will be greyed-out and not responsive to UI events.
    """)

    visible = Bool(True, help="""
    Whether the component will be visible and a part of a layout.
    """)

    width = NonNegativeInt(default=None, help="""
    The width of the component (in pixels).

    This can be either fixed or preferred width, depending on width sizing policy.
    """)

    height = NonNegativeInt(default=None, help="""
    The height of the component (in pixels).

    This can be either fixed or preferred height, depending on height sizing policy.
    """)

    min_width = NonNegativeInt(default=None, help="""
    Minimal width of the component (in pixels) if width is adjustable.
    """)

    min_height = NonNegativeInt(default=None, help="""
    Minimal height of the component (in pixels) if height is adjustable.
    """)

    max_width = NonNegativeInt(default=None, help="""
    Minimal width of the component (in pixels) if width is adjustable.
    """)

    max_height = NonNegativeInt(default=None, help="""
    Minimal height of the component (in pixels) if height is adjustable.
    """)

    margin = Tuple(Int, Int, Int, Int, default=(0, 0, 0, 0), help="""
    Allows to create additional space around the component.
    """).accepts(Tuple(Int, Int), lambda v_h: (v_h[0], v_h[1], v_h[0], v_h[1])) \
        .accepts(Int, lambda m: (m, m, m, m))

    width_policy = Either(Auto, Enum(SizingPolicy), default="auto", help="""
    Describes how the component should maintain its width.

    ``"auto"``
        Use component's preferred sizing policy.

    ``"fixed"``
        Use exactly ``width`` pixels. Component will overflow if it can't fit in the
        available horizontal space.

    ``"fit"``
        Use component's preferred width (if set) and allow it to fit into the available
        horizontal space within the minimum and maximum width bounds (if set). Component's
        width neither will be aggressively minimized nor maximized.

    ``"min"``
        Use as little horizontal space as possible, not less than the minimum width (if set).
        The starting point is the preferred width (if set). The width of the component may
        shrink or grow depending on the parent layout, aspect management and other factors.

    ``"max"``
        Use as much horizontal space as possible, not more than the maximum width (if set).
        The starting point is the preferred width (if set). The width of the component may
        shrink or grow depending on the parent layout, aspect management and other factors.

    """)

    height_policy = Either(Auto, Enum(SizingPolicy), default="auto", help="""
    Describes how the component should maintain its height.

    ``"auto"``
        Use component's preferred sizing policy.

    ``"fixed"``
        Use exactly ``height`` pixels. Component will overflow if it can't fit in the
        available vertical space.

    ``"fit"``
        Use component's preferred height (if set) and allow to fit into the available
        vertical space withing the minimum and maximum height bounds (if set). Component's
        height neither will be aggressively minimized nor maximized.

    ``"min"``
        Use as little vertical space as possible, not less than the minimum height (if set).
        The starting point is the preferred height (if set). The height of the component may
        shrink or grow depending on the parent layout, aspect management and other factors.

    ``"max"``
        Use as much vertical space as possible, not more than the maximum height (if set).
        The starting point is the preferred height (if set). The height of the component may
        shrink or grow depending on the parent layout, aspect management and other factors.

    """)

    aspect_ratio = Either(Enum("auto"), Float, default=None, help="""
    Describes the proportional relationship between component's width and height.

    This works if any of component's dimensions are flexible in size. If set to
    a number, ``width / height = aspect_ratio`` relationship will be maintained.
    Otherwise, if set to ``"auto"``, component's preferred width and height will
    be used to determine the aspect (if not set, no aspect will be preserved).

    """)

    sizing_mode = Enum(SizingMode, default=None, help="""
    How the component should size itself.

    This is a high-level setting for maintaining width and height of the component. To
    gain more fine grained control over sizing, use ``width_policy``, ``height_policy``
    and ``aspect_ratio`` instead (those take precedence over ``sizing_mode``).

    Possible scenarios:

    ``"fixed"``
        Component is not responsive. It will retain its original width and height
        regardless of any subsequent browser window resize events.

    ``"stretch_width"``
        Component will responsively resize to stretch to the available width, without
        maintaining any aspect ratio. The height of the component depends on the type
        of the component and may be fixed or fit to component's contents.

    ``"stretch_height"``
        Component will responsively resize to stretch to the available height, without
        maintaining any aspect ratio. The width of the component depends on the type
        of the component and may be fixed or fit to component's contents.

    ``"stretch_both"``
        Component is completely responsive, independently in width and height, and
        will occupy all the available horizontal and vertical space, even if this
        changes the aspect ratio of the component.

    ``"scale_width"``
        Component will responsively resize to stretch to the available width, while
        maintaining the original or provided aspect ratio.

    ``"scale_height"``
        Component will responsively resize to stretch to the available height, while
        maintaining the original or provided aspect ratio.

    ``"scale_both"``
        Component will responsively resize to both the available width and height, while
        maintaining the original or provided aspect ratio.

    """)

    background = Color(default=None, help="""
    Background color of the component.
    """)

    # List in order for in-place changes to trigger changes, ref: https://github.com/bokeh/bokeh/issues/6841
    css_classes = List(String, help="""
    A list of CSS class names to add to this DOM element. Note: the class names are
    simply added as-is, no other guarantees are provided.

    It is also permissible to assign from tuples, however these are adapted -- the
    property will always contain a list.
    """).accepts(Seq(String), lambda x: list(x))

    @warning(FIXED_SIZING_MODE)
    def _check_fixed_sizing_mode(self):
        if self.sizing_mode == "fixed" and (self.width is None or self.height is None):
            return str(self)

    @warning(FIXED_WIDTH_POLICY)
    def _check_fixed_width_policy(self):
        if self.width_policy == "fixed" and self.width is None:
            return str(self)

    @warning(FIXED_HEIGHT_POLICY)
    def _check_fixed_height_policy(self):
        if self.height_policy == "fixed" and self.height is None:
            return str(self)

    @error(MIN_PREFERRED_MAX_WIDTH)
    def _min_preferred_max_width(self):
        min_width = self.min_width if self.min_width is not None else 0
        width     = self.width     if self.width     is not None else min_width
        max_width = self.max_width if self.max_width is not None else width

        if not (min_width <= width <= max_width):
            return str(self)

    @error(MIN_PREFERRED_MAX_HEIGHT)
    def _min_preferred_max_height(self):
        min_height = self.min_height if self.min_height is not None else 0
        height     = self.height     if self.height     is not None else min_height
        max_height = self.max_height if self.max_height is not None else height

        if not (min_height <= height <= max_height):
            return str(self)

@abstract
class HTMLBox(LayoutDOM):
    ''' A component which size is determined by its HTML content.

    '''

class Spacer(LayoutDOM):
    ''' A container for space used to fill an empty spot in a row or column.

    '''

QuickTrackSizing = Either(Enum("auto", "min", "max"), Int)

RowSizing = Either(
    QuickTrackSizing,
    Struct(policy=Enum("auto", "min", "max"), align=Enum(TrackAlign)),
    Struct(policy=Enum("fixed"), height=Int, align=Enum(TrackAlign)),
    Struct(policy=Enum("flex"), factor=Float, align=Enum(TrackAlign)))

ColSizing = Either(
    QuickTrackSizing,
    Struct(policy=Enum("auto", "min", "max"), align=Enum(TrackAlign)),
    Struct(policy=Enum("fixed"), width=Int, align=Enum(TrackAlign)),
    Struct(policy=Enum("flex"), factor=Float, align=Enum(TrackAlign)))

IntOrString = Either(Int, String) # XXX: work around issue #8166

class GridBox(LayoutDOM):

    children = List(Tuple(Instance(LayoutDOM), Int, Int), default=[], help="""
    """)

    rows = Either(QuickTrackSizing, Dict(IntOrString, RowSizing), default="auto", help="""
    """)

    cols = Either(QuickTrackSizing, Dict(IntOrString, ColSizing), default="auto", help="""
    """)

    spacing = Either(Int, Tuple(Int, Int), default=0, help="""
    """)

@abstract
class Box(LayoutDOM):
    ''' Abstract base class for Row and Column. Do not use directly.

    '''

    def __init__(self, *args, **kwargs):

        if len(args) > 0 and "children" in kwargs:
            raise ValueError("'children' keyword cannot be used with positional arguments")
        elif len(args) > 0:
            kwargs["children"] = list(args)

        super(Box, self).__init__(**kwargs)

    @warning(EMPTY_LAYOUT)
    def _check_empty_layout(self):
        from itertools import chain
        if not list(chain(self.children)):
            return str(self)

    @warning(BOTH_CHILD_AND_ROOT)
    def _check_child_is_also_root(self):
        problems = []
        for c in self.children:
            if c.document is not None and c in c.document.roots:
                problems.append(str(c))
        if problems:
            return ", ".join(problems)
        else:
            return None

    children = List(Instance(LayoutDOM), help="""
    The list of children, which can be other components including plots, rows, columns, and widgets.
    """)

    spacing = Int(default=0, help="""
    """)


class Row(Box):
    ''' Lay out child components in a single horizontal row.

    Children can be specified as positional arguments, as a single argument
    that is a sequence, or using the ``children`` keyword argument.
    '''

    cols = Either(QuickTrackSizing, Dict(IntOrString, ColSizing), default="auto", help="""
    """)

class Column(Box):
    ''' Lay out child components in a single vertical row.

    Children can be specified as positional arguments, as a single argument
    that is a sequence, or using the ``children`` keyword argument.
    '''

    rows = Either(QuickTrackSizing, Dict(IntOrString, RowSizing), default="auto", help="""
    """)

class WidgetBox(Column):
    ''' Create a column of bokeh widgets with predefined styling.

    '''

class Panel(Model):
    ''' A single-widget container with title bar and controls.

    '''

    title = String(default="", help="""
    The text title of the panel.
    """)

    child = Instance(LayoutDOM, help="""
    The child widget. If you need more children, use a layout widget, e.g. a ``Column``.
    """)

class Tabs(LayoutDOM):
    ''' A panel widget with navigation tabs.

    '''

    __example__ = "sphinx/source/docs/user_guide/examples/interaction_tab_panes.py"

    tabs = List(Instance(Panel), help="""
    The list of child panel widgets.
    """).accepts(List(Tuple(String, Instance(LayoutDOM))),
                 lambda items: [ Panel(title=title, child=child) for (title, child) in items ])

    tabs_location = Enum(Location, default="above", help="""
    The location of the buttons that activate tabs.
    """)

    active = Int(0, help="""
    The index of the active tab.
    """)

    callback = Instance(Callback, help="""
    A callback to run in the browser whenever the button is activated.
    """)

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
