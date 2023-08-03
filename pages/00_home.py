import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import solara
import solara.lab
import random
import numpy as np
# Assuming you have already imported the necessary libraries and read the data
dfwm = pd.read_csv("data/portalWebMaps_Test.csv")
dfsubset = dfwm[['map_title', 'service_title', 'layer_url', 'share_settings', 'number_of_views']]
dfsubset_san = dfsubset.sort_values(by=['number_of_views'], ascending=False)
dfsubset_san['layer_url'] = dfsubset_san['layer_url'].str.replace(r'^.*services/([^/]*)/.*$', r'\1', regex=True)
#num_breaks = 4
#dfsubset_san['views_class_breaks'] = pd.cut(dfsubset_san['number_of_views'], bins=num_breaks, precision=0)
#dfsubset_san['quant_views'] = pd.qcut(dfsubset_san['number_of_views'], q=12, labels=[12,11,10,9,8,7,6,5,4,3,2,1])
#print(dfsubset_san['quant_views'])

dfsubset_san['quant_views'] = (((dfsubset_san['number_of_views'] / 250000) * 80) + 30)


map_titles = dfsubset_san['map_title'].unique()
webMaps = []
map_title_to_color = {}
mttc = {}
for title in map_titles:
    # Generate random RGB values in the range [0, 255]
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    # Convert RGB values to a valid color format (e.g., HEX or RGBA)
    color = f'rgba({red},{green},{blue},0.3)'
    k_color = f'rgba({red},{green},{blue},0.8)' # You can use HEX format if needed
    # Assign the random color to the map_title
    map_title_to_color[title] = color
    mttc[title] = k_color
    webMaps.append(title)

select_wm = solara.reactive(webMaps)
dfsubset_san['colors'] = [map_title_to_color[title] for title in dfsubset_san['map_title']]
dfsubset_san['k_colors'] = [mttc[title] for title in dfsubset_san['map_title']]
dfsubset_san['map_color'] = 'rgba(155,194,156,0.5)'
dfsubset_san['service_color'] = 'rgba(199,85,46,0.5)'

mapdict = dfsubset_san[['map_title', 'map_color']].to_dict('records')
layerdict = dfsubset_san[['layer_url', 'service_color']].to_dict('records')

#dfdict = dfsubset_san.to_dict()
#print(dfdict)

tab_index = solara.reactive(0)

#spring layout
G = nx.Graph()
G = nx.from_pandas_edgelist(dfsubset_san, 'map_title', 'layer_url')

# 1. Convert the NetworkX graph into a Plotly graph object
pos = nx.kamada_kawai_layout(G)  # Adjust the layout algorithm as needed

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=0.5, color='#000000'),
    hoverinfo='none',
    mode='lines',
)

node_x = []
node_y = []
node_text = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_info = str(node) + "<br># of connections: " + str(len(list(G.neighbors(node))))
    node_text.append(node_info)

#print([10 + 5 * len(list(G.neighbors(node))) for node in G.nodes()])

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    text=node_text,
    hoverinfo='text',
    mode='markers+text',
    marker=dict(
        #size=[10 + 5 * len(list(G.neighbors(node))) for node in G.nodes()],
        size=dfsubset_san['quant_views'],
        color=dfsubset_san['k_colors']
    ),
)

# 2. Create the figure using Plotly Graph Objects
fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
    showlegend=False,
    hovermode='closest',
    margin=dict(b=0, l=0, r=0, t=0),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    height=975
))

nodes = []
links = []

def add_node(node_name):
    if node_name not in nodes:
        nodes.append(node_name)

# Helper function to add links
def add_link(source, target, value, views, color):
    add_node(source)
    add_node(target)
    add_node(views)
    links.append({"source": nodes.index(source), "target": nodes.index(target), "views": nodes.index(views), "color": color, 'value': value})

# Process the enumerated_items and add nodes and links to the Sankey diagram
for item in zip(dfsubset_san['map_title'], dfsubset_san['layer_url'], dfsubset_san['number_of_views'], dfsubset_san['service_title'], dfsubset_san['colors']):
    source = f"{item[0]}"
    target = f"{item[1]}: {item[3]}"
    value = 1
    color = f"{item[4]}"  # Or you can use a value based on some criteria if available in your data
    views = f"{item[2]}"
    add_link(source, target, value, views, color)  # First link from source to target
    add_link(target, views, value, views, color)  # Second link from target to views

# Create the Sankey diagram trace with colors for the links
sankey_trace = go.Sankey(
    arrangement="freeform",
    node=dict(
        pad=30,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=nodes,
        color=[link["color"] for link in links]

    ),
    link=dict(
        source=[link["source"] for link in links],
        target=[link["target"] for link in links],
        value=[link["value"] for link in links],
        color=[link["color"] for link in links]
    )
)

# Create the figure and plot the Sankey diagram
sanfig = go.Figure(data=[sankey_trace])

sanfig.update_layout(title_text="Web Maps Connections to Layers in Portal",
                     font_size=18,
                     height=4000)

@solara.component
def Page():
    with solara.Column() as main:
        with solara.AppBarTitle():
            solara.Text("Crook County GIS Portal Map")

        with solara.lab.Tabs(background_color="#0A2E52", dark=True):

            with solara.lab.Tab("Sankey Layout", icon_name="mdi-chart-line"):
                with solara.Card(style="height: 1000px;"):

                    solara.FigurePlotly(sanfig)

            with solara.lab.Tab("Kamada Kawai Layout", icon_name="mdi-chart-line"):
                with solara.Card(style="height: 1000px;"):

                    solara.FigurePlotly(fig)

        with solara.Sidebar():
            solara.SelectMultiple("Web Maps", select_wm, webMaps)
            solara.Markdown(f"**Selected**: {select_wm.value}")

    return main
