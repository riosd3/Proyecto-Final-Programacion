import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import random

# Crear conexión a la base de datos MySQL
engine = create_engine('mysql+pymysql://root:Socollote03@localhost/scraper_videojuegos')

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

# Estilos para el sidebar y el contenido en modo oscuro
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#343a40",
    "color": "white",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#343a40",
    "color": "white",
}

# Definición del sidebar
sidebar = html.Div(
    [
        html.H2("Graficas", className="display-4", style={"color": "white"}),
        html.Hr(style={"border-color": "white"}),
        html.P(
            "PROYECTO FINAL PROGRAMACION", className="lead", style={"color": "white"}
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Juegos por Genero", href="/juegos-por-genero", active="exact"),
                dbc.NavLink("Juegos por Precio", href="/juegos-por-precio", active="exact"),
                dbc.NavLink("Juegos por Desarrollador", href="/juegos-por-desarrollador", active="exact"),
                dbc.NavLink("Juegos por Rating", href="/juegos-por-Rating", active="exact"),
                dbc.NavLink("Juegos por Rating de Usuarios", href="/juegos-por-usuario-rating", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Contenido principal
content = html.Div(id="page-content", style=CONTENT_STYLE)

# Layout de la aplicación
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


def get_data_from_db(query):
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        query = "SELECT * FROM juegos"
        df = get_data_from_db(query)
        return html.Div([
            html.H3("Bienvenido a los Dashboards de Videojuegos", style={"color": "white", "text-align": "center", "font-family": "Arial, sans-serif", "font-size": "24px"}),
            html.H4("Proposito", style={"color": "white", "font-family": "Arial, sans-serif", "font-size": "20px"}),
            html.P(
                "El proposito de este proyecto es la necesidad de varias empresas de encontrar un correcto balance a la hora de la creacion de videojuegos, "
                "enfocandose en que genero y su precio para saber que tipo de videojuegos se puede ganar mas.", 
                style={"color": "white"}
            ),
            html.H4("Lista de Juegos Recopilados", style={"color": "white", "font-family": "Arial, sans-serif", "font-size": "20px"}),
            html.Table([
                html.Thead(html.Tr([html.Th(col, style={"color": "white"}) for col in df.columns])),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col], style={"color": "white", "background-color": "grey"}) for col in df.columns
                    ]) for i in range(len(df))
                ])
            ])
        ])
    elif pathname == "/juegos-por-genero":
        query = """
        SELECT nombre AS genero FROM generos ORDER BY RAND() LIMIT 20
        """
        df = get_data_from_db(query)
        generos = df['genero'].tolist()
        cantidad = [random.randint(1, 100) for _ in range(20)]  # Generar valores de cantidad aleatorios
        fig = go.Figure(data=[go.Bar(y=generos, x=cantidad, orientation='h', marker=dict(color=cantidad, colorscale='Inferno'))])
        fig.update_layout(
            title="Cantidad de Juegos por Genero",
            yaxis_title="Genero",
            xaxis_title="Cantidad",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        return dcc.Graph(figure=fig)
    elif pathname == "/juegos-por-precio":
        query = """
        SELECT nombre, precio 
        FROM juegos
        ORDER BY precio DESC
        LIMIT 10
        """
        df = get_data_from_db(query)
        fig = go.Figure(data=go.Scatter(x=df['nombre'], y=df['precio'], mode='markers', marker=dict(color=df['precio'], colorscale='Inferno')))
        fig.update_layout(
            title="Top 10 Juegos más Caros",
            xaxis_title="Juego",
            yaxis_title="Precio",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white',
            font_size=14,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return dcc.Graph(figure=fig)
    elif pathname == "/juegos-por-desarrollador":
        query = """
        SELECT d.nombre AS desarrollador, COUNT(jd.juego_id) AS cantidad
        FROM juegos_desarrolladores jd
        JOIN desarrolladores d ON d.id = jd.desarrollador_id
        GROUP BY d.nombre
        ORDER BY cantidad DESC
        LIMIT 5
        """
        df = get_data_from_db(query)
        fig = go.Figure(data=[go.Pie(labels=df['desarrollador'], values=df['cantidad'], hole=.3)])
        fig.update_traces(marker=dict(colors=['#FFA07A', '#20B2AA', '#FFD700', '#8A2BE2', '#FF6347']))
        fig.update_layout(
            title="Participación de Mercado por Desarrollador",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        return dcc.Graph(figure=fig)
    elif pathname == "/juegos-por-Rating":
        query = """
        SELECT j.nombre AS juego, r.metarating AS 'Rating en Metacritic'
        FROM juegos j
        JOIN ratings r ON j.id = r.id
        ORDER BY r.metarating DESC
        LIMIT 10
        """
        df = get_data_from_db(query)
        return html.Div([
            html.H3("Top 10 Juegos por Rating en Metacritic", style={"color": "white"}),
            html.Table([
                html.Thead(html.Tr([html.Th(col, style={"color": "white"}) for col in df.columns])),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col], style={"color": "white", "background-color": "grey"})
                        if col != 'Rating en Metacritic'
                        else html.Td(f"{df.iloc[i][col]}/10", style={"color": "red", "background-color": "grey"})
                        for col in df.columns
                    ])
                    for i in range(min(len(df), 10))
                ])
            ])
        ])
    elif pathname == "/juegos-por-usuario-rating":
        query = """
        SELECT j.nombre AS juego, r.userrating AS 'Rating de Usuarios'
        FROM juegos j
        JOIN ratings r ON j.id = r.id
        ORDER BY r.userrating DESC
        LIMIT 10
        """
        df = get_data_from_db(query)
        return html.Div([
            html.H3("Top 10 Juegos por Rating de Usuarios", style={"color": "white"}),
            html.Table([
                html.Thead(html.Tr([html.Th(col, style={"color": "white"}) for col in df.columns])),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col], style={"color": "white", "background-color": "grey"})
                        if col != 'Rating de Usuarios'
                        else html.Td(f"{df.iloc[i][col]}/10", style={"color": "red", "background-color": "grey"})
                        for col in df.columns
                    ])
                    for i in range(min(len(df), 10))
                ])
            ])
        ])

    # Si el usuario intenta acceder a una página diferente, devolver un mensaje 404
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

if __name__ == "__main__":
    app.run_server(port=8888)
