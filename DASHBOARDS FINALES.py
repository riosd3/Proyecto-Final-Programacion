import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, dash_table
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

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
                dbc.NavLink("Juegos por Rating", href="/juegos-por-Rating", active="exact")
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


def datadb(query):
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render(ruta):
    if ruta == "/":
        query = "SELECT * FROM juegos"
        df = datadb(query)
        return html.Div([
            html.H3("Bienvenido a los Dashboards de Videojuegos", style={"color": "white", "text-align": "center", "font-family": "Arial, sans-serif", "font-size": "24px"}),
            html.H4("Proposito", style={"color": "white", "font-family": "Arial, sans-serif", "font-size": "20px"}),
            html.P(
                "El proposito de este proyecto es la necesidad de varias empresas de encontrar un correcto balance a la hora de la creacion de videojuegos, "
                "enfocandose en que genero y su precio para saber que tipo de videojuegos se puede ganar mas.", 
                style={"color": "white"}
            ),
            html.H4("Lista de Juegos Recopilados", style={"color": "white", "font-family": "Arial, sans-serif", "font-size": "20px"}),
            html.Div([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_cell={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    }
                )
            ])
        ])
    elif ruta == "/juegos-por-genero":
        query = """
        SELECT g.nombre AS genero, COUNT(jg.juego_id) AS cantidad
        FROM generos g
        JOIN juegos_generos jg ON g.id = jg.genero_id
        GROUP BY g.nombre
        ORDER BY cantidad DESC
        LIMIT 20
        """
        df = datadb(query)
        generos = df['genero'].tolist()
        cantidad = df['cantidad'].tolist()
        
        fig_barras = go.Figure(data=[go.Bar(y=generos, x=cantidad, orientation='h', marker=dict(color=cantidad, colorscale='Inferno'))])
        fig_barras.update_layout(
            title="Cantidad de Juegos por Genero",
            yaxis_title="Genero",
            xaxis_title="Cantidad",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        
        fig_pie = go.Figure(data=[go.Pie(labels=generos, values=cantidad, hole=.3)])
        fig_pie.update_layout(
            title="Proporción de Juegos por Genero",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        
        top_generos = df.head(3)
        cards = [
            dbc.Card(
                dbc.CardBody([
                    html.H5(f"Género: {row['genero']}", className="card-title"),
                    html.P(f"Cantidad: {row['cantidad']}", className="card-text")
                ]),
                color="dark", inverse=True
            ) for index, row in top_generos.iterrows()
        ]
        
        return html.Div([
            dcc.Graph(figure=fig_barras),
            dcc.Graph(figure=fig_pie),
            html.Div(cards, className="d-flex justify-content-around mt-4")
        ])
    elif ruta == "/juegos-por-precio":
        query = """
        SELECT nombre, precio 
        FROM juegos
        ORDER BY precio DESC
        LIMIT 10
        """
        df = datadb(query)
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
    elif ruta == "/juegos-por-desarrollador":
        query = """
        SELECT d.nombre AS desarrollador, COUNT(jd.juego_id) AS cantidad
        FROM juegos_desarrolladores jd
        JOIN desarrolladores d ON d.id = jd.desarrollador_id
        GROUP BY d.nombre
        ORDER BY cantidad DESC
        LIMIT 5
        """
        df = datadb(query)
        fig = go.Figure(data=[go.Pie(labels=df['desarrollador'], values=df['cantidad'], hole=.3)])
        fig.update_traces(marker=dict(colors=['#FFA07A', '#20B2AA', '#FFD700', '#8A2BE2', '#FF6347']))
        fig.update_layout(
            title="Participación de Mercado por Desarrollador",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        
        developers_info = {
            "Capcom": "Capcom es conocido por sus juegos de acción y aventura como Resident Evil y Monster Hunter.",
            "Nintendo": "Nintendo se especializa en juegos de familia y aventuras como Super Mario y The Legend of Zelda.",
            "Telltale Games": "Telltale Games es famoso por sus juegos de aventuras gráficas basadas en historias como The Walking Dead y The Wolf Among Us.",
            "Konami": "Konami es conocido por sus juegos de acción y deportes como Metal Gear Solid y Pro Evolution Soccer.",
            "Square Enix": "Square Enix se especializa en juegos de rol y aventuras como Final Fantasy y Kingdom Hearts."
        }
        
        cards = [
            dbc.Card(
                dbc.CardBody([
                    html.H5(developer, className="card-title"),
                    html.P(info, className="card-text")
                ]),
                color="dark", inverse=True
            ) for developer, info in developers_info.items()
        ]

        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(cards, className="d-flex justify-content-around mt-4")
        ])
    elif ruta == "/juegos-por-Rating":
        query = """
        SELECT j.nombre AS juego, r.metarating AS 'Rating en Metacritic'
        FROM juegos j
        JOIN ratings r ON j.id = r.id
        ORDER BY r.metarating DESC
        LIMIT 10
        """
        df = datadb(query)
        top_juegos = df.head(3)
        
        juegos_info = {
            "The Legend of Zelda: Ocarina of Time": "Género: Acción/Aventura",
            "Grand Theft Auto V": "Género: Acción/Aventura",
            "The Witcher 3: Wild Hunt": "Género: RPG"
        }
        
        cards = [
            dbc.Card(
                dbc.CardBody([
                    html.H5(juego, className="card-title"),
                    html.P(f"Rating en Metacritic: {row['Rating en Metacritic']}", className="card-text"),
                    html.P(juegos_info.get(juego, ""), className="card-text")
                ]),
                color="dark", inverse=True
            ) for juego, row in top_juegos.iterrows()
        ]

        fig = go.Figure(data=[go.Bar(x=df['juego'], y=df['Rating en Metacritic'], marker=dict(color=df['Rating en Metacritic'], colorscale='Viridis'))])
        fig.update_layout(
            title="Top 10 Juegos por Rating en Metacritic",
            xaxis_title="Juego",
            yaxis_title="Rating",
            plot_bgcolor='#343a40',
            paper_bgcolor='#343a40',
            font_color='white'
        )
        return html.Div([
            dcc.Graph(figure=fig),
            html.Div(cards, className="d-flex justify-content-around mt-4")
        ])
    elif ruta == "/juegos-por-usuario-rating":
        query = """
        SELECT j.nombre AS juego, r.user_rating AS 'Rating de Usuarios'
        FROM juegos j
        JOIN ratings r ON j.id = r.id
        ORDER BY r.user_rating DESC
        LIMIT 10
        """
        df = datadb(query)
        top_juegos = df.head(3)
        
        juegos_info = {
            "The Legend of Zelda: Ocarina of Time": "Género: Acción/Aventura",
            "Grand Theft Auto V": "Género: Acción/Aventura",
            "The Witcher 3: Wild Hunt": "Género: RPG"
        }
        
        cards = [
            dbc.Card(
                dbc.CardBody([
                    html.H5(juego, className="card-title"),
                    html.P(f"Rating de Usuarios: {row['Rating de Usuarios']}", className="card-text"),
                    html.P(juegos_info.get(juego, ""), className="card-text")
                ]),
                color="dark", inverse=True
            ) for juego, row in top_juegos.iterrows()
        ]

        

if __name__ == "__main__":
    app.run_server(debug=True)
