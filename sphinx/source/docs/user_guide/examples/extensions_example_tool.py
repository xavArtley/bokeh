from bokeh.core.properties import Instance
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, Tool
from bokeh.plotting import figure
from bokeh.util.compiler import TypeScript

output_file('tool.html')

TS_CODE = """
import * as p from "core/properties"
import {GestureTool, GestureToolView} from "models/tools/gestures/gesture_tool"
import {GestureEvent} from "core/ui_events"
import {ColumnDataSource} from "models/sources/column_data_source"

export class DrawToolView extends GestureToolView {
  model: DrawTool

  //this is executed when the pan/drag event starts
  _pan_start(_ev: GestureEvent): void {
    this.model.source.data = {x: [], y: []}
  }

  //this is executed on subsequent mouse/touch moves
  _pan(ev: GestureEvent): void {
    const frame = this.plot_view.frame
    const {sx, sy} = ev
    if (!frame.bbox.contains(sx,sy)){return}
    const x = frame.xscales['default'].invert(sx)
    const y = frame.yscales['default'].invert(sy)

    this.model.source.get_array('x').push(x)
    this.model.source.get_array('y').push(y)
    this.model.source.change.emit()
  }

  // this is executed then the pan/drag ends
  _pan_end(_ev: GestureEvent):void {}
}

export class DrawTool extends GestureTool {
  source: ColumnDataSource

  tool_name= "Drag Span"
  icon= "bk-tool-icon-lasso-select"
  event_type= "pan" as "pan"
  default_order= 12

  static initClass(): void {
    this.prototype.default_view = DrawToolView
    this.prototype.type = "DrawTool"
    this.define({
    source: [p.Any],
    })
  }
}
DrawTool.initClass()
"""

class DrawTool(Tool):
    __implementation__ = TypeScript(TS_CODE)
    source = Instance(ColumnDataSource)

source = ColumnDataSource(data=dict(x=[], y=[]))

plot = figure(x_range=(0,10), y_range=(0,10), tools=[DrawTool(source=source)])
plot.title.text ="Drag to draw on the plot"
plot.line('x', 'y', source=source)

show(plot)
