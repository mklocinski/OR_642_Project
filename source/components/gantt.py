from dash import html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from source.utilities import viz


gantt_chart = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(id='show-me'),
                    dbc.Row([
                        html.H5('Select Date'),
                        dcc.DatePickerRange(
                            id='filter-date',
                            month_format='MMMM Y',
                            end_date_placeholder_text='MMMM Y')
                    ]),
                    dbc.Row([
                        html.H5('Select Working Group'),
                        dcc.Dropdown(id='filter-working-group')
                    ]),
                    dbc.Row([
                        html.H5('Select Author'),
                        dcc.Dropdown(id='filter-author')
                ])], width=3),
                dbc.Col([
                    html.Div(id="gantt-chart")
                ], width=9)
    ])
])


@callback(
    Output('filter-date', 'start_date'),
    Output('filter-date', 'end_date'),
    Output('filter-working-group', 'options'),
    Output('filter-author', 'options'),
    Input('model-output', 'data')
)
def create_filter_options(model_output):

    df = pd.DataFrame.from_dict(model_output)
    date_opts = df['Date'].unique()
    wgroup_opts = df['Working Group'].unique()
    author_opts = df['Authors'].unique()
    f_date = viz.reformat_date_string(min(date_opts), "%m/%d/%Y", "%Y-%m-%d")
    f_wgroup = [{'label': i, 'value': i} for i in wgroup_opts]
    f_author = [{'label': i, 'value': i} for i in author_opts]

    return f_date, f_date, f_wgroup, f_author


@callback(
    Output('gantt-chart', 'children'),
    Input('model-output', 'data'),
    Input('filter-date', 'start_date'),
    Input('filter-date', 'end_date'),
    Input('filter-working-group', 'value'),
    Input('filter-author', 'value')
)
def create_gantt_chart(model_output, start_date, end_date, wg_filter, author_filter):
    df = pd.DataFrame.from_dict(model_output)
    formatted = viz.format_model_output(df)
    filtered = viz.apply_filters(formatted, [start_date, end_date], wg_filter, author_filter)
    gantt_chart = viz.make_gantt(filtered)

    return dcc.Graph(figure=gantt_chart)