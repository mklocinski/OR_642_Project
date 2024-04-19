from dash import dash_table, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
from source.model import MK_PuLP, GH_PuLP, AH_PuLP
from source.utilities import viz



engine = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                        dbc.Button('Run Model', id='run-selected-model-button', class_name='dark-emphasis-button', n_clicks=0)
                    ]),
                html.Br(),
                dbc.Row([
                    dcc.Loading(
                                html.Div(id='show-model-status'),
                                type="dot",
                    )
                ])
            ])
        ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                children=[html.Div(id='model-result-message')]
            )
        ],width=12)
    ])
])

@callback(
    Output('model-result-message','children'),
    Output('model-output', 'data'),
    Input('run-selected-model-button','n_clicks'),
    State('selected-model','value'),
    State('uploaded-data', 'data')
)
def run_model(clicks, selected_model, stored_data):
    if clicks == 0:
        raise PreventUpdate
    else:
        if selected_model == 'model_1':
            df = pd.DataFrame.from_dict(stored_data['Scraped'])
            selected_model = MK_PuLP.run_MK_PuLP(df)
        if selected_model == 'model_2':
            df1 = pd.DataFrame.from_dict(stored_data['Abstract Data'])
            df2 = pd.DataFrame.from_dict(stored_data['Schedule Data'])
            df3 = pd.DataFrame.from_dict(stored_data['Preference Data'])
            selected_model = GH_PuLP.run_GH_PuLP(df1, df2, df3)
        if selected_model == 'model_3':
            df1 = pd.DataFrame.from_dict(stored_data['Abstract Data'])
            df2 = pd.DataFrame.from_dict(stored_data['Schedule Data'])
            df3 = pd.DataFrame.from_dict(stored_data['Preference Data'])
            selected_model = AH_PuLP.run_AH_PuLP(df1, df2, df3)
        return selected_model[0], selected_model[1].to_dict(orient='records')
