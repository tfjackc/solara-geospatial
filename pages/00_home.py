import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import solara
import solara.lab
import random
# Assuming you have already imported the necessary libraries and read the data
from huggingface_hub import Repository

repo = Repository(
    local_dir="csv_data",
    repo_type="dataset",
    clone_from="tfjackc/csv_data",
    token=True
)
repo.git_pull()


#dfwm = pd.read_csv("data/portalWebMaps_Test.csv")
dfwm = pd.read_csv("portalWebMaps_Test.csv")
dfsubset = dfwm[['map_title', 'service_title', 'layer_url', 'share_settings', 'number_of_views']]
tab_index = solara.reactive(0)

#spring layout
G = nx.Graph()
G = nx.from_pandas_edgelist(dfsubset, 'map_title', 'service_title')

# 1. Convert the NetworkX graph into a Plotly graph object
pos = nx.spring_layout(G)  # Adjust the layout algorithm as needed

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

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    text=node_text,
    hoverinfo='text',
    mode='markers+text',
    marker=dict(
        size=[10 + 5 * len(list(G.neighbors(node))) for node in G.nodes()],
    ),
)

# 2. Create the figure using Plotly Graph Objects
fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
    showlegend=False,
    hovermode='closest',
    margin=dict(b=0, l=0, r=0, t=0),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    height=975
))

# sankey layout
dfsubset_san = dfwm[['map_title', 'service_title', 'share_settings', 'layer_url', 'number_of_views']]
dfsubset_san = dfsubset_san.sort_values(by=['number_of_views'], ascending=False)

# 3. Define the Solara component as before
@solara.component
def Page():
    with solara.Column() as main:
        with solara.AppBarTitle():
            solara.Text("Crook County GIS Portal Map")



        with solara.lab.Tabs(background_color="#0A2E52", dark=True):

            with solara.lab.Tab("Sankey Layout", icon_name="mdi-chart-line"):
                with solara.Card(style="height: 1000px;"):
                    map_titles = dfsubset_san['map_title'].unique()
                    print(map_titles)
                    webMaps = []
                    map_title_to_color = {}
                    for title in map_titles:
                        # Generate random RGB values in the range [0, 255]
                        red = random.randint(0, 255)
                        green = random.randint(0, 255)
                        blue = random.randint(0, 255)
                        # Convert RGB values to a valid color format (e.g., HEX or RGBA)
                        color = f'rgba({red},{green},{blue},0.8)'  # You can use HEX format if needed
                        # Assign the random color to the map_title
                        map_title_to_color[title] = color
                        webMaps.append(title)

                    select_wm = solara.reactive(webMaps)
                    # Create a node list containing unique labels and corresponding indices
                    node_labels = select_wm.value + list(dfsubset_san['layer_url'])
                    node_indices = list(range(len(select_wm.value))) + list(range(len(dfsubset_san['layer_url'])))

                    # Create a dictionary to map the labels to indices for faster lookup
                    label_to_index = {label: idx for idx, label in enumerate(node_labels)}

                    # Create a link list with source, target, and value columns
                    link_list = []
                    for index, row in dfsubset_san.iterrows():
                        source = label_to_index[row['map_title']]
                        target = label_to_index[row['layer_url']]
                        link_list.append({
                            'source': source,
                            'target': target,
                            'value': 1  # Or you can use a value based on some criteria if available in your data
                        })

                    # Create the Sankey diagram
                    sanfig = go.Figure(data=[go.Sankey(
                        valueformat=".0f",
                        valuesuffix="TWh",
                        # Define nodes
                        node=dict(
                            pad=15,
                            thickness=15,
                            line=dict(color="black", width=0.5),
                            label=node_labels,
                            color=['rgba(255,0,255, 0.8)' if label == "magenta" else 'blue' for label in node_labels]
                        ),
                        # Add links
                        link=dict(
                            source=[link['source'] for link in link_list],
                            target=[link['target'] for link in link_list],
                            value=[link['value'] for link in link_list],
                            label=None,
                            color=[map_title_to_color[node_labels[link['source']]] for link in link_list]
                            # You can adjust the color here if needed
                        ))
                    ])

                    sanfig.update_layout(title_text="Web Maps Connections to Layers in Portal",
                                         font_size=18,
                                         height=4000)
                    solara.FigurePlotly(sanfig)

            with solara.lab.Tab("Spring Layout", icon_name="mdi-chart-line"):
                with solara.Card(style="height: 1000px;"):

                    solara.FigurePlotly(fig)

        with solara.Sidebar():
            solara.SelectMultiple("Web Maps", select_wm, webMaps)
            solara.Markdown(f"**Selected**: {select_wm.value}")

    return main
