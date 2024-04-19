from dash import html, callback, Output, Input, State, dcc, dash_table
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
from source.components import engine
from source.utilities import global_vars, texts


layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.H1("Run Model")
            ),
            html.Br(),
            dbc.Row([
                html.P(texts.rmp_sidebar_para_1),
                html.P(texts.rmp_sidebar_para_2),
                html.Br(),
                html.Br(),
                html.H5("Select Model"),
                dcc.RadioItems([
                                {'label': v['label'], 'value': v['value']}
                            for k,v in texts.rmp_model_descriptions.items()
                            ],
                            value='model_1', id='selected-model', className='radio'),
                html.Br(),
                html.Br(),
                dbc.Button('Review Output', href='/review-output', id='review-output-button', class_name='button'),
                html.H5("or", style={'textAlign': 'center'}),
                dbc.Button("Download",id='download-button', class_name='button'),
                dcc.Download(id="download-output")
            ])
        ], width=3, class_name='sidebar'),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                   dbc.Row([
                       dbc.Col([
                           html.H5('Selected Model')
                       ], width=6),
                        dbc.Col([
                           html.Div(id='selected-model-name')
                       ], width=6),
                ]),
                dbc.Row([
                       dbc.Col([
                           html.H5('Description')
                       ], width=6),
                        dbc.Col([
                           html.Div(id='selected-model-description')
                       ], width=6)
                ])
                ], width=6, class_name='outline-emphasis'),
                dbc.Col([
                    engine.engine
                ], width=5, class_name='dark-emphasis')
            ]),
            dash_table.DataTable(
                id='show-model-output-table',
                columns=[{'name': i,
                          'id': i} for i in global_vars.OUTPUT_COLUMNS.keys()],
                page_size=5,
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    'fontSize': '8pt',
                }
            )
        ], width=8)
    ])
])



dash.register_page("Run Model", layout=layout, path="/run-model", order=3)

@callback(
    Output('review-output-button','disabled'),
    Output('download-button','disabled'),
    Input('model-output','modified_timestamp')
)
def disable_review_download(model_output):
    status = True if model_output is None else False
    return status, status

@callback(
        Output('selected-model-name','children'),
        Output('selected-model-description','children'),
        Input('selected-model','value')
)
def select_model(selected_view):
        return texts.rmp_model_descriptions[selected_view]['label'], texts.rmp_model_descriptions[selected_view]['description']

@callback(
    Output('show-model-output-table', 'data'),
    Input('model-output', 'modified_timestamp'),
    State('model-output', 'data')
)
def output_from_model(output_time, model_data):
    if output_time is None:
        raise PreventUpdate
    else:
        reordered_output = pd.DataFrame.from_dict(model_data)
        reordered_output = reordered_output[[i for i in global_vars.OUTPUT_COLUMNS.keys()]]
        return reordered_output.to_dict('records')

@callback(
    Output('download-output', 'data'),
    Input("download-button", "n_clicks"),
    State('model-output', 'data'),
    prevent_initial_call=True,
)
def prepare_download(clicks, model_output):
    df = pd.DataFrame.from_dict(model_output)
    filename = 'MORS Schedule Optimizer Output_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
    return dcc.send_data_frame(df.to_excel, filename, sheet_name="Schedule")