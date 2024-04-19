from dash import html, dcc, callback, Output, Input, State
import pandas as pd
from source.utilities import texts, global_vars


def data_validation(df_name, df):
    if df_name not in global_vars.INPUT_COLUMNS.keys():
        msg = df_name + " - " + texts.udp_invalid_submission_file
        validity = 'invalid'
    else:
        schema = global_vars.INPUT_COLUMNS[df_name].keys()
        missing_cols = {k for k in schema}.difference(df.columns)
        col_list = ', '.join(missing_cols)
        validity = 'valid' if len(missing_cols) == 0 else 'invalid'
        msg = df_name + " - " + texts.udp_valid_submission if len(
            missing_cols) == 0 else df_name + " " + texts.udp_invalid_submission_data + col_list
    return msg, validity


def validation_banner(validity_check):
    if validity_check[1] == 'valid':
        return html.Div(children=[validity_check[0]], style={'background': '#90EE90',
                                                             'font-size': '10px',
                                                             'border': '3px solid #3A5311',
                                                             'border-radius': '10px',
                                                             'padding': '15px',
                                                             'margin': '2px'})
    if validity_check[1] == 'invalid':
        return html.Div(children=[validity_check[0]], style={'background': '#FF7F7F',
                                                             'font-size': '10px',
                                                             'border': '3px solid #990F02',
                                                             'border-radius': '10px',
                                                             'padding': '15px',
                                                             'margin': '2px'})


def generate_sessions(sess_start_stop_times, interval):
    all_sessions = []
    for sess in sess_start_stop_times:
        x = [d.to_pydatetime().strftime('%m/%d/%Y %I:%M %p') for d in pd.date_range(sess[0], sess[1], freq=interval)]
        all_sessions.extend(x[:-1])
    return all_sessions

def model_result(model_status):
    pulp_outputs = {1:"Optimal solution found", 0:"Not solved",
                    -1:"Infeasible", -2:"Unbounded", -3:"Undefined"}
    color_status = {1:"#90EE90", 0:"white",
                    -1:"red", -2:"red", -3:"red"}
    return html.Center(html.Div(children=[pulp_outputs[model_status]],
                    style={'color':'white',
                           'background-color':color_status[model_status],
                           'font-size':'14px',
                           'border-radius': '10px',
                           'padding': '15px',
                           'margin': '2px'
                           }))