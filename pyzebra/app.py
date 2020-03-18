import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, gridplot, row
from bokeh.models import (
    BasicTicker,
    Button,
    ColumnDataSource,
    DataRange1d,
    Dropdown,
    Grid,
    HoverTool,
    Image,
    Line,
    LinearAxis,
    PanTool,
    Plot,
    Range1d,
    ResetTool,
    SaveTool,
    Spinner,
    TextInput,
    Toggle,
    WheelZoomTool,
)

import pyzebra

IMAGE_W = 256
IMAGE_H = 128

doc = curdoc()

global curent_h5_data, current_index


def update_image():
    current_image = curent_h5_data[current_index]
    proj_v_line_source.data.update(x=np.arange(0, IMAGE_W) + 0.5, y=np.mean(current_image, axis=0))
    proj_h_line_source.data.update(x=np.mean(current_image, axis=1), y=np.arange(0, IMAGE_H) + 0.5)
    image_source.data.update(image=[current_image])
    index_spinner.value = current_index


def filelist_callback(_attr, _old, new):
    global curent_h5_data, current_index
    data = pyzebra.read_detector_data(new)
    curent_h5_data = data
    current_index = 0
    update_image()


filelist = Dropdown()
filelist.on_change("value", filelist_callback)


def fileinput_callback(_attr, _old, new):
    h5meta_list = pyzebra.read_h5meta(new)
    file_list = h5meta_list["filelist"]
    filelist.menu = file_list


fileinput = TextInput()
fileinput.on_change("value", fileinput_callback)
fileinput.value = "/Users/zaharko/1work/ZeBRa/ZebraSoftware/python_for_zebra/hdfdata/1.cami"


def index_spinner_callback(_attr, _old, new):
    global current_index
    if 0 <= new < curent_h5_data.shape[0]:
        current_index = new
        update_image()


index_spinner = Spinner(value=0)
index_spinner.on_change("value", index_spinner_callback)

plot = Plot(
    x_range=Range1d(0, IMAGE_W, bounds=(0, IMAGE_W)),
    y_range=Range1d(0, IMAGE_H, bounds=(0, IMAGE_H)),
    plot_height=IMAGE_H * 3,
    plot_width=IMAGE_W * 3,
    toolbar_location="left",
)

# ---- tools
plot.toolbar.logo = None

hovertool = HoverTool(tooltips=[("intensity", "@image")], names=["image_glyph"])

plot.add_tools(PanTool(), WheelZoomTool(maintain_focus=False), SaveTool(), ResetTool(), hovertool)
plot.toolbar.active_scroll = plot.tools[1]

# ---- axes
plot.add_layout(LinearAxis(), place="above")
plot.add_layout(LinearAxis(major_label_orientation="vertical"), place="right")

# ---- grid lines
plot.add_layout(Grid(dimension=0, ticker=BasicTicker()))
plot.add_layout(Grid(dimension=1, ticker=BasicTicker()))

# ---- rgba image glyph
image_source = ColumnDataSource(
    dict(image=[np.zeros((1, 1), dtype="float32")], x=[0], y=[0], dw=[IMAGE_W], dh=[IMAGE_H],)
)

image_glyph = Image(image="image", x="x", y="y", dw="dw", dh="dh")
image_renderer = plot.add_glyph(image_source, image_glyph, name="image_glyph")

# ---- projections
proj_v = Plot(
    x_range=plot.x_range,
    y_range=DataRange1d(),
    plot_height=200,
    plot_width=IMAGE_W * 3,
    toolbar_location=None,
)

proj_v.add_layout(LinearAxis(major_label_orientation="vertical"), place="right")
proj_v.add_layout(LinearAxis(major_label_text_font_size="0pt"), place="below")

proj_v.add_layout(Grid(dimension=0, ticker=BasicTicker()))
proj_v.add_layout(Grid(dimension=1, ticker=BasicTicker()))

proj_v_line_source = ColumnDataSource(dict(x=[], y=[]))
proj_v.add_glyph(proj_v_line_source, Line(x="x", y="y", line_color="steelblue"))

proj_h = Plot(
    x_range=DataRange1d(),
    y_range=plot.y_range,
    plot_height=IMAGE_H * 3,
    plot_width=200,
    toolbar_location=None,
)

proj_h.add_layout(LinearAxis(), place="above")
proj_h.add_layout(LinearAxis(major_label_text_font_size="0pt"), place="left")

proj_h.add_layout(Grid(dimension=0, ticker=BasicTicker()))
proj_h.add_layout(Grid(dimension=1, ticker=BasicTicker()))

proj_h_line_source = ColumnDataSource(dict(x=[], y=[]))
proj_h.add_glyph(proj_h_line_source, Line(x="x", y="y", line_color="steelblue"))


def prev_button_callback():
    global current_index
    if current_index > 0:
        current_index -= 1
    update_image()


prev_button = Button(label="Previous")
prev_button.on_click(prev_button_callback)


def next_button_callback():
    global current_index
    if current_index < curent_h5_data.shape[0] - 1:
        current_index += 1
    update_image()


next_button = Button(label="Next")
next_button.on_click(next_button_callback)


def animate():
    next_button_callback()


def animate_toggle_callback(active):
    global cb
    if active:
        cb = doc.add_periodic_callback(animate, 300)
    else:
        doc.remove_periodic_callback(cb)


animate_toggle = Toggle(label="Animate")
animate_toggle.on_click(animate_toggle_callback)

layout_image = gridplot([[proj_v, None], [plot, proj_h]], merge_tools=False)

doc.add_root(
    column(
        fileinput,
        filelist,
        layout_image,
        row(prev_button, next_button),
        row(index_spinner, animate_toggle),
    )
)
