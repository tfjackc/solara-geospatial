from typing import Any, Dict, Optional, cast
from pathlib import Path
import plotly
import solara
import leafmap
from leafmap.toolbar import change_basemap
from solara.components.file_drop import FileInfo
import os
cables = 'sub_cables.geojson'
zoom = solara.reactive(2)
center = solara.reactive((20, 0))
#layer = solara.reactive(cables)

class Map(leafmap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        #self.load_data()
        self.add_stac_gui()

    #def load_data(self):
     #   self.add_geojson() # in_geojson=layer.value, layer_name='sub_cables')



@solara.component
def Page():


    insert_css, set_insert_css = solara.use_state(True)

    css = """
        .v-toolbar__content {
            justify-content: center;
        }
        .v-toolbar__title {
            font-size: 25px;
        }
        """

    # html = """
    #     <h1>Hello World</h1>
    # """

    content, set_content = solara.use_state(b"")
    filename, set_filename = solara.use_state("")
    file, set_file = solara.use_state(cast(Optional[Path], None))
    path, set_path = solara.use_state(cast(Optional[Path], None))
    directory, set_directory = solara.use_state(Path("~").expanduser())

    def on_file(file: FileInfo):
        set_filename(file["name"])
        f = file["file_obj"]
        set_content(f.read(100))
        print(f"File Name: {filename}")
        #layer.value = filename
        #load_data(filename)
        #Map.load_data(filename)
        #my_map.add_geojson(in_geojson=filename, layer_name='geojson_layer')

    with solara.VBox() as main:

        if insert_css:
            solara.Style(css)
            with solara.AppBar():
                solara.AppBarTitle("Solara Mapping")
            with solara.Column():

                with solara.Sidebar():
                    can_select = solara.ui_checkbox("Enable select")

                    def reset_path():
                        set_path(None)
                        set_file(None)

                    solara.use_memo(reset_path, [can_select])
                    solara.FileBrowser(directory, on_directory_change=set_directory, on_path_select=set_path,
                                       on_file_open=set_file, can_select=can_select)
                    solara.Info(f"You are in directory: {directory}")
                    solara.Info(f"You selected path: {path}")
                    solara.Info(f"You opened file: {file}")

                    solara.FileDrop(
                        label="Drag and drop a file here",
                        on_file=on_file)
                    if content:
                        solara.Info(f"File {filename}")

                with solara.VBox():
                    #solara.Markdown("Hello World")
                    Map.element(  # type: ignore
                        zoom=zoom.value,
                        on_zoom=zoom.set,
                        center=center.value,
                        on_center=center.set,
                        scroll_wheel_zoom=True,
                        toolbar_ctrl=True,
                        data_ctrl=False,
                        height="780px"
                    )
                    solara.Text(f"Zoom: {zoom.value}")
                    solara.Text(f"Center: {center.value}")

            #solara.HTML(tag="div", unsafe_innerHTML=html)



    return main