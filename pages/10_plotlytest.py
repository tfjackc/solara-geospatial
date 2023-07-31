import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import solara

# Assuming you have already imported the necessary libraries and read the data
dfwm = pd.read_csv(r"portalWebMaps_Test.csv")
dfsubset = dfwm[['map_title', 'service_title', 'layer_url']]

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
    mode='lines'
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
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        size=[10 + 5 * len(list(G.neighbors(node))) for node in G.nodes()],
    )
)

@solara.component
def Page():
    with solara.Column() as main:
        with solara.AppBarTitle():
            solara.Text("Crook County GIS Portal Map")

        with solara.Card(style="height: 1000px;"):
            selection_data, set_selection_data = solara.use_state(None)
            click_data, set_click_data = solara.use_state(None)
            hover_data, set_hover_data = solara.use_state(None)
            unhover_data, set_unhover_data = solara.use_state(None)
            deselect_data, set_deselect_data = solara.use_state(None)
            # Create the figure
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=0, l=0, r=0, t=0),
                                xaxis=dict(showgrid=False, zeroline=False),
                                yaxis=dict(showgrid=False, zeroline=False),
                                height=975
                            ))

            solara.FigurePlotly(
                fig, on_selection=set_selection_data, on_click=set_click_data, on_hover=set_hover_data, on_unhover=set_unhover_data, on_deselect=set_deselect_data
            )

        with solara.Sidebar():
            solara.Markdown(
                f"""
            # Plot Data
            ## selection
            ```
            {selection_data}
            ```

            ## click
            ```
            {click_data}
            ```

            ## hover
            ```
            {hover_data}
            ```

            ## unhover
            ```
            {unhover_data}
            ```

            ## deselect
            ```
            {deselect_data}
            ```


            """
            )

    return main
