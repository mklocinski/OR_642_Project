from dash import dcc, html, callback, Input, Output, State, dash_table
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
from source.components import uploader
from source.utilities import global_vars, viz, texts

layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.H1("Upload data")
            ),
            html.Br(),
            dbc.Row([
                html.P(texts.udp_sidebar_para_1),
                html.Br(),
                html.Br(),
                html.H5("Next:"),
                dbc.Button('Run Model', href='/run-model', id='run-model-button', class_name='button')
            ])
        ], width=3, className='sidebar'),
        dbc.Col([
            uploader.uploader,
            dcc.Tabs(id="input-data-review", value='Abstract Data', children=[
                    dcc.Tab(label='Scraped', value='Scraped'),
                    dcc.Tab(label='Abstract Data', value='Abstract Data'),
                    dcc.Tab(label='Schedule Data', value='Schedule Data'),
                    dcc.Tab(label='Preference Data', value='Preference Data')
                ]),
            html.Br(),
            dash_table.DataTable(
                            id='show-input-data-table',
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

dash.register_page("Upload", layout=layout, path="/upload-abstract-data", order=2)


@callback(
    Output('run-model-button','disabled'),
    Input('all-valid','modified_timestamp')
)
def disable_run_model(validity):
    if validity is None:
        status = True
    elif validity >= 3:
        status = False
    else:
        status = True
    return status

@callback(
    Output('show-input-data-table','data'),
    Output('show-input-data-table','columns'),
    Input('input-data-review', 'value'),
    Input('uploaded-data', 'data')
)
def show_input_data(tab_value, input_data):
    cols = [i for i in global_vars.INPUT_COLUMNS[tab_value].keys()]
    if input_data is None or input_data == {}:
        reordered_input = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame.from_dict(input_data[tab_value])
        reordered_input = df[cols]
    return reordered_input.to_dict('records'), [{'name': i,'id': i} for i in cols]
