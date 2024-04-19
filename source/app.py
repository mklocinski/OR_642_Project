from dash import Dash, dcc, html
import dash
import dash_bootstrap_components as dbc
from components import navbar
from pages import main_page


external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__package__,
            external_stylesheets=external_stylesheets,
            use_pages=True,
            suppress_callback_exceptions=True)

dash.register_page("Main", layout=main_page.main_layout, path='/')


app.layout = dbc.Container(children=[
            dcc.Store(id='session-blocks'),
            dcc.Store(id='raw-data'),
            dcc.Store(id='uploaded-data'),
            dcc.Store(id='all-valid'),
            dcc.Store(id='chosen-model'),
            dcc.Store(id='model-output'),
            navbar.make_navbar,
            dash.page_container
    ], fluid=True)




if __name__ == '__main__':
    app.run(debug=True)
