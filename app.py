import dash
from dash import dcc
from dash import html
import numpy as np
from dash.dependencies import Input, Output, State
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import datasets
from sklearn.svm import SVC
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dbscan import generate_figure, load_measurement, get_channels_list, find_files_in_folder
import os
#options for measurements to select

selectable_measurements = [{'label':meas, 'value':meas} for meas in find_files_in_folder()]

app = dash.Dash()
app.title = "DBSCAN"
app.layout = html.Div(
        children=[
                # .container class is fixed, .container.scalable is scalable
                html.Div(
                        className="banner",
                        children=[
                                # Change App Name here
                                html.Div(
                                        className="container scalable",
                                        children=[
                                                # Change App Name here
                                                html.H2(
                                                        id="banner-title",
                                                        children=[
                                                                html.A(
                                                                        "DBSCAN CENTROID FINDER",

                                                                )
                                                        ],
                                                ),
                                        ],
                                )
                        ],
                ),
                html.Div(
                        id="body",
                        className="container scalable",
                        children=[
                                html.Div(
                                        id="app-container",
                                        # className="row",
                                        children=[
                                                html.Div(
                                                        # className="three columns",
                                                        id="left-column",
                                                        children=[
                                                                dbc.Card(
                                                                        id="first-card",
                                                                        children=[
                                                                                dcc.Dropdown(id='select-meas-dropdown', options=selectable_measurements),
                                                                                html.Button('Select measurement', id='select-measurement-btn'),
                                                                                dcc.Dropdown(id='select-channel-sig-rpm'),
                                                                                dcc.Dropdown(id='select-channel-sig-maf'),
                                                                                dcc.Dropdown(id='select-channel-sig-temp'),
                                                                                html.H3('Hyper-parameters'),
                                                                                dcc.Slider(
                                                                                       
                                                                                        id="epsilon-temp",
                                                                                        marks={
                                                                                                key * 100 : str(key * 100) for key in range(11)
                                                                                        },
                                                                                        min=1,
                                                                                        max=1000,

                                                                                        value=100,
                                                                                       
                                                                                ),
                                                                                dcc.Slider(
                                                                                       
                                                                                        id="sample-threshold-temp",
                                                                                        marks={
                                                                                               key*5:str(key*5) for key in range(5)
                                                                                        },
                                                                                        min=0.2,
                                                                                        max=25,
                                                                                        value=19,

                                                                                ),
                                                                                html.H4('Generate JSON for centroids'),
                                                                                html.Button('Click to Create', id='create-file-btn')
                                                                        ],
                                                                ),

                                                        ],
                                                ),
                                                html.Div(
                                                        id="div-graphs",
                                                        children=dcc.Graph(
                                                                id="graph-sklearn-svm",
                                                                figure=dict(
                                                                        layout=dict(
                                                                                plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                                                                        )
                                                                ),
                                                        ),
                                                ),
                                        ],
                                )
                        ],
                ),
        ]
)


@app.callback(
        Output("div-graphs", "children"),
        [
                Input("epsilon-temp", "value"),
                Input("sample-threshold-temp", "value"),
                Input('create-file-btn', 'n_clicks'),
                State("select-channel-sig-rpm", "value"),
                State("select-channel-sig-maf", "value"),
                State("select-channel-sig-temp", "value"),
               
        ],
        prevent_initial_call=True
)
def update_figure( eps_3, min_samples_3, btn_click, sig_rpm, sig_maf, sig_temp):
    global data
    return generate_figure(eps_3, min_samples_3, btn_click, data, sig_rpm, sig_maf, sig_temp)


@app.callback(
        Output("select-channel-sig-rpm", "options"),
        Output("select-channel-sig-maf", "options"),
        Output("select-channel-sig-temp", "options"),
       
        [
                Input('select-measurement-btn', 'n_clicks'),
                State('select-meas-dropdown', 'value')
        ],
        prevent_initial_call=True
)
def select_dropdowns(btn_click, meas_name):
        global data
        data = load_measurement(f'{os.path.expanduser("~/Desktop/cluster")}/{meas_name}')
        channels_list= [{'label':signal, 'value':signal} for signal in get_channels_list(data)]
        return channels_list, channels_list, channels_list

# Running the server
if __name__ == "__main__":
    app.run_server()
