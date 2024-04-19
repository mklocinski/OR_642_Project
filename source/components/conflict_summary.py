from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from source.utilities import viz


conflicts_chart = html.Div([
                    dbc.Row([html.Div(id='conflict-chart')]),
                    dbc.Row([
                    dbc.Col([
                        html.H5("Presentation Conflicts"),
                        html.I("Presentation is booked more than once for the same time slot and day"),
                        html.Div(id='talk-conflict')
                    ]),
                    dbc.Col([
                        html.H5("Author Conflicts"),
                        html.I("Author is booked more than once the same time slot and day"),
                        html.Div(id='author-conflict')
                    ]),
                    dbc.Col([
                        html.H5("Working Group Conflicts"),
                        html.I("Working Group has multiple presentations occurring during the same time slot and day"),
                        html.Div(id='wgroup-conflict')
                    ])
                ])
            ])

@callback(
    Output('conflict-chart', 'children'),
    Output('talk-conflict', 'children'),
    Output('author-conflict', 'children'),
    Output('wgroup-conflict', 'children'),
    Input('model-output', 'data')
)
def create_conflict_chart(model_output):
    df = pd.DataFrame.from_dict(model_output)
    formatted = viz.format_model_output(df)
    data_prep = viz.conflict_summary(formatted)
    conflict_chart = viz.plot_conflict_summary(data_prep[0])

    wc = viz.df_to_datatable(data_prep[1]) if len(data_prep[1]) > 0 else "No Conflicts"
    ac = viz.df_to_datatable(data_prep[2]) if len(data_prep[2]) > 0 else "No Conflicts"
    wgc= viz.df_to_datatable(data_prep[3]) if len(data_prep[3]) > 0 else "No Conflicts"
    return dcc.Graph(figure=conflict_chart), wc, ac, wgc
