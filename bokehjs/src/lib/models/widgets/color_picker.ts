import * as p from "core/properties"
import {input} from 'core/dom'
import {InputWidget, InputWidgetView} from 'models/widgets/input_widget'
import {Color} from 'core/types'


export class ColorPickerView extends InputWidgetView {
  model: ColorPicker

  protected input: HTMLInputElement

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.name.change, () => this.input.name = this.model.name || "")
    this.connect(this.model.properties.color.change, () => this.input.value = this.model.color)
    this.connect(this.model.properties.disabled.change, () => this.input.disabled = this.model.disabled)
  }

  render(): void {
    super.render()

    this.input = input({
      type: "color",
      class: "bk-input",
      name: this.model.name,
      value: this.model.color,
      disabled: this.model.disabled,
    })
    this.input.addEventListener("change", () => this.change_input())
    this.el.appendChild(this.input)
  }

  change_input(): void {
    this.model.color = this.input.value
    super.change_input()
  }
}

export namespace ColorPicker {
  export interface Attrs extends InputWidget.Attrs {
    color: Color
  }

  export interface Props extends InputWidget.Props {
    color: p.Property<Color>
  }
}

export interface ColorPicker extends ColorPicker.Attrs {}

export class ColorPicker extends InputWidget {

  properties: ColorPicker.Props

  static initClass(): void {
    this.prototype.type = "ColorPicker"
    this.prototype.default_view = ColorPickerView

    this.define({
      color: [p.Color, "#000000"],
    })
  }
}
ColorPicker.initClass()
