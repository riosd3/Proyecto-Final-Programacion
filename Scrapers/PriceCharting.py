import pandas as pd
import requests
from bs4 import BeautifulSoup

# URL de la página web a scrapear
url = 'https://www.pricecharting.com/console/nes?sort=highest_price'

# Realizar la solicitud GET a la URL
response = requests.get(url)

# Comprobar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Lista para almacenar los datos
    games_data = []

    # Encontrar todos los elementos tr de la tabla
    game_rows = soup.find_all('tr')

    # Iterar sobre cada fila de la tabla
    for row in game_rows:
        # Obtener el nombre del juego
        name = row.find('td', class_='title').a.text.strip()

        # Obtener el precio
        price = row.find('td', class_='price').span.text.strip()

        # Agregar los datos a la lista
        games_data.append({'Nombre del juego': name, 'Precio': price})

    # Convertir la lista de datos en un DataFrame de Pandas
    df = pd.DataFrame(games_data)

    # Guardar el DataFrame en un archivo CSV
    csv_file = 'pricecharting_games.csv'
    df.to_csv(csv_file, index=False)

    print("Scraping completado. Los datos han sido guardados en", csv_file)
else:
    print("Error al realizar la solicitud GET a la URL:", url)
