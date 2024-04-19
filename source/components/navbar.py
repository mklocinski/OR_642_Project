from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc

make_navbar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", id='home-nav', class_name='navlink'),
                dbc.NavLink("Upload Abstract Data", href="/upload-abstract-data", id='abstract-upload-nav', class_name='navlink'),
                dbc.NavLink("Run Model", href="/run-model", id='model-nav', class_name='navlink'),
                dbc.NavLink("Review Output", href="/review-output", id='review-nav', class_name='navlink'),
                dbc.DropdownMenu(
                            [dbc.DropdownMenuItem("Input Data Template"),
                             dbc.DropdownMenuItem("User Guide"),
                             dbc.DropdownMenuItem("Model Documentation")],
                            label="More",
                            nav=True,
                            color="secondary",
                            style={'color':'white'}
                        )
            ], horizontal='end',
        class_name='navbar'),
        html.Br(),
    ]
)


@callback(
    Output('abstract-upload-nav','disabled'),
    Output('model-nav', 'disabled'),
    Output('review-nav', 'disabled'),
    Input('session-blocks', 'modified_timestamp'),
    Input('uploaded-data', 'modified_timestamp'),
    Input('model-output', 'modified_timestamp')
)
def toggle_navlinks(session_data, abstract_data, model_data):
    abstract_data_link_status = True if session_data is None else False
    model_link_status = True if abstract_data is None else False
    review_link_status = True if model_data is None else False
    return abstract_data_link_status, model_link_status, review_link_status
