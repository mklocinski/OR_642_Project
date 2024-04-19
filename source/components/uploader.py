import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import base64
import io
from source.utilities import viz, global_vars, app_functions

uploader_custom_css = {'lineHeight': '40px',
                       'borderWidth': '1px',
                       'borderStyle': 'dashed',
                       'borderRadius': '5px',
                       'textAlign': 'center'}

uploader = html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style=uploader_custom_css
                )
            ], width=8),
            dbc.Col([
                dbc.Button('Validate and Save', id='commit-data-button', class_name='minor-button')
            ], width=3),
            dbc.Col([], width=9)
        ]),
    html.Br(),
    dcc.Loading(
        dbc.Row(id='data-validation-message')
    )], className='light-emphasis')



@callback(
    Output('commit-data-button','disabled'),
    Input('raw-data','modified_timestamp')
)
def disable_commit_data(stored_data):
    status = True if stored_data is None else False
    return status


@callback(
            Output('raw-data', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('session-blocks','data')
)
def store_upload(contents, filename, date, session_data):
    if contents is None:
        raise PreventUpdate
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded), sheet_name=None)
    store = {k:v.to_dict('records') for k,v in df.items()}
    if 'Schedule Data' not in store.keys() and session_data is not None:
        date_data = [[v['Session Start', v['Session End']]] for k, v in session_data.items()]
        store['Schedule Data'] = app_functions.generate_sessions(date_data, '30min')[0]
    elif 'Schedule Data' not in store.keys() and session_data is None:
        store['Schedule Data'] = {}
    return store

@callback(
    Output('uploaded-data','data'),
    Output('data-validation-message', 'children'),
    Output('all-valid','data'),
    Input('commit-data-button', 'n_clicks'),
    State('raw-data','data'),
    config_prevent_initial_callbacks=True
)
def commit_changes(clicks, input_data):
    if clicks is None:
        raise PreventUpdate
    else:
        msg_display = []
        valid_inputs = 0
        for worksheet in global_vars.INPUT_COLUMNS.keys():
            df = pd.DataFrame.from_dict(input_data[worksheet])
            validation = app_functions.data_validation(worksheet, df)
            valid_inputs += 1 if validation[1] == 'valid' else 0
            msg_display.append(dbc.Col([app_functions.validation_banner(validation)], width=4))

    return input_data, dbc.Row(msg_display), valid_inputs

