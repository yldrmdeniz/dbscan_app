import numpy as np
import asammdf as mdf
import plotly.graph_objects as go
# from plotly.graph_objs import Scene, XAxis, YAxis, ZAxis
from sklearn.cluster import DBSCAN

from dash import html
from dash import dcc
import os


def find_files_in_folder():
        file_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop/cluster') 
        available_files = [file for file in os.listdir(file_path) if (file.endswith('.dat') or file.endswith('.mf4'))] 
        return available_files



def load_measurement(file_path):
        data = mdf.MDF(rf'{file_path}')
        return data


def get_channels_list(data):
        return data.channels_db



def generate_figure(eps_3, min_samples_3, btn_click, data, sig_rpm, sig_maf, sig_temp):
    #print(eps_1, min_samples_1, eps_2, min_samples_2, eps_3, min_samples_3)
#     data = mdf.MDF(r'BMEP_Mapping_20220420_115032.dat')
    sig_rpm = data.get(sig_rpm).samples.astype(int)
    sig_maf = data.get(sig_maf).samples.astype(int)
    sig_temp = data.get(sig_temp).samples.astype(int)
    #sig_temp = np.delete(sig_temp, 0)
    sig_rpm_rs = sig_rpm.reshape(-1, 1)
    sig_maf_rs = sig_maf.reshape(-1, 1)
    sig_temp_rs = sig_temp.reshape(-1, 1)

    eps_3_weighed = eps_3 / 100
    db_temp = DBSCAN(eps=eps_3_weighed, min_samples=min_samples_3).fit(np.array([sig_temp_rs.flatten(), sig_maf_rs.flatten()]).T)

    idx_to_remove_3 = np.where(db_temp.labels_ == -1)[0]
    fig = go.Figure()

    sig_rpm_filtered =sig_rpm_rs.flatten()
    sig_maf_filtered = sig_maf_rs.flatten()
    sig_temp_filtered = sig_maf_rs.flatten()
    labels = list(set(db_temp.labels_))
    labels.remove(-1) if -1 in labels else ...

    ctr = 1
    results_dict = {}
    for label in labels:
        fig.add_trace(go.Scatter3d(x=sig_rpm_filtered[db_temp.labels_ == label], y=sig_maf_filtered[db_temp.labels_ == label],
                                   z=sig_temp_filtered[db_temp.labels_ == label],
                                   mode='markers',
                                   name=str(ctr),
                                   showlegend=False))
        x_center = np.round(sig_rpm_filtered[db_temp.labels_ == label].mean(),2)
        y_center = np.round(sig_maf_filtered[db_temp.labels_ == label].mean(),2)
        z_center = np.round(sig_temp_filtered[db_temp.labels_ == label].mean(),2)
        fig.add_trace(go.Scatter3d(x=[x_center],
                                   y=[y_center],
                                   z=[z_center],
                                   mode='markers',
                                   marker=dict(color='red', size=12),
                                   name=f'centroid of cluster {ctr} rpm, maf, temp {x_center, y_center, z_center}',
                                   ))

        results_dict[f'cluster_{ctr}'] = (x_center, y_center, z_center)
        ctr += 1

    scene = {
                    "xaxis" : {"title": "RPM"},
                    "yaxis" : {"title": "Mass Air Flow"},
                    "zaxis" : {"title": "Temperature "},
                    "camera": {
                            "center": {"x": 0, "y": 0, "z": -0.25},
                            "eye"   : {"x": 1.5, "y": 1.5, "z": 0.5},
                            "up"    : {"x": 0, "y": 0, "z": 1},
                    }
            }
    fig.update_layout(dict(scene=scene))

    import os
    desktop = os.path.expanduser("~/Desktop")
    # the above is valid on Windows (after 7) but if you want it in os normalized form:

    if btn_click:

        import json
        g = f'{desktop}/result_for_eps_{eps_3_weighed}_{min_samples_3}.json'
        with open(g, 'x') as outfile:
            json.dump(results_dict, outfile, indent=2)

    return [
            html.Div(
                    id="svm-graph-container",

                    className="graph-wrapper",
                    children=[dcc.Graph(id="graph-sklearn-svm", figure=fig),
                              ],
            ),

    ]
