from dash import html, callback, Input, Output, dcc
import dash
import dash_bootstrap_components as dbc
from source.components import gantt, conflict_summary

layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.H1("Review Output")
            ),
            html.Br(),
            dbc.Row([
                html.P("Check for any conflicts or unexpected results."),
                html.Br(),
                html.Br(),
                html.H5("Review Method"),
                dcc.RadioItems([
                                {'label': 'Gantt Chart', 'value': 'gantt_chart'},
                                {'label': 'Conflicts', 'value': 'conflict_chart'}
                            ],
                            value='gantt_chart', id='selected-view')
            ])
        ], width=3),
        dbc.Col([
            html.Div(id='view-holder')
        ], width=9)
    ])
])

dash.register_page("Review Output", layout=layout, path="/review-output", order=4)

@callback(
        Output('view-holder','children'),
        Input('selected-view','value')
)
def update_view(selected_view):
        if selected_view == 'conflict_chart':
                return conflict_summary.conflicts_chart
        if selected_view == 'gantt_chart':
                return gantt.gantt_chart