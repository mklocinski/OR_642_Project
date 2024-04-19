import dash
from dash import html, callback, Input, State, Output
import dash_bootstrap_components as dbc
from datetime import datetime, date
from source.utilities import texts



main_layout = html.Div(

        dbc.Container(children=[
            dbc.Row([
        dbc.Col([
                    dbc.Row([html.H1(texts.hp_title)
                             ], className='titlerow'),
                    html.Br(),
                    dbc.Row([
                        html.P(texts.hp_sidebar_para_1),
                        dbc.Button('Start', href='/upload-abstract-data',id='enter-abstract-data-button', class_name='button')
                    ])
                ], width=3, class_name='sidebar'),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                html.H3('Enter session block information')
                            ]),
                            dbc.Row([
                                html.P('For each session block, enter the date on which it occurs and its start and end times.')
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(id="date-input", placeholder="mm/dd/YYYY", type="text")
                                ], width=3),
                                dbc.Col([
                                    dbc.Input(id="timeslot-start-input", placeholder="HH:MM AM/PM", type="text")
                                ], width=3),
                                dbc.Col([
                                    dbc.Input(id="timeslot-end-input", placeholder="HH:MM AM/PM", type="text")
                                ], width=3),
                                dbc.Col([
                                    dbc.Button('+',  id='commit-session-data', class_name='minor-button')
                                ], width=3)
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Checklist(
                                            options=[
                                                {"label": "I'm including session information as a separate tab in my abstract data file", "value": 1}
                                            ],
                                            value=[2],
                                            id="session-data-in-file",
                                            switch=True,
                                        )
                            ])
                        ])
                    ], class_name='light-emphasis'),
                    dbc.Row([
                        html.Div(html.Pre(id='entered-session-data'))
                    ], class_name='outline-emphasis')

                ], width=8, class_name='standard-container')
            ])
            ])

)



@callback(
    Output('session-blocks','data'),
    Output('entered-session-data','children'),
    Input('commit-session-data','n_clicks'),
    State('session-blocks','modified_timestamp'),
    State('session-blocks','data'),
    State('date-input','value'),
    State('timeslot-start-input','value'),
    State('timeslot-end-input','value'),
    State('entered-session-data','children')
)
def save_session_block_data(click, store_status, store_data, session_date, session_start, session_end, display_string):
    if click is None:
        session_string = 'No session data entered'
        return dash.no_update, session_string
    else:
        if store_status is None:
            session_info = {click: {'date': session_date,
                                    'Session Start': datetime.strptime(session_date + ' ' + session_start, '%m/%d/%Y %I:%M %p'),
                                    'Session End': datetime.strptime(session_date + ' ' + session_end, '%m/%d/%Y %I:%M %p')}}
            session_string = str(session_date) + "- Session Start: " + str(session_start) + ", Session End: " + str(session_end)
            return session_info, session_string
        else:
            store_data[session_date] = {'start': session_start, 'end': session_end}
            session_info = store_data
            new_string = str(session_date) + "- Session Start: " + str(session_start) + ", Session End: " + str(session_end)
            display_string = '' if display_string == 'No session data entered' else display_string
            session_string = '\n\n'.join([display_string, new_string])
            return session_info, session_string

@callback(
    Output('session-blocks', 'data', allow_duplicate=True),
    Input('session-data-in-file', 'value'),
    config_prevent_initial_callbacks=True
)
def register_toggle_input(toggle_value):
    if toggle_value == [2]:
        return dash.no_update
    else:
        return {}


@callback(
    Output('enter-abstract-data-button','disabled'),
    Input('session-blocks', 'modified_timestamp'),
    Input('session-data-in-file', 'value')
)
def disable_enter_abstract_data_button(session_data, toggle_value):
    if session_data is None:
        status = True
    else:
        status = False
    return status


