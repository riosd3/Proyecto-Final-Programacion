import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from FilterCheck import pagesAvailability

class SteamCharts():
    def __init__(self):
        # Configuración del navegador
        if not pagesAvailability["steamcharts"]["filtered"]:
            self.main_url = pagesAvailability["steamcharts"]["main_url"]
            s = Service(ChromeDriverManager().install())
            options = Options()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument("--window-size=1020,1200")
            self.navegador = webdriver.Chrome(service=s, options=options)
            self.inst_status = True
        else:
            self.inst_status = False

    def scrap(self):
        # Navegación a la página SteamCharts
        self.navegador.get(self.main_url)
        time.sleep(5)

        # Búsqueda del juego "Counter-Strike"
        search_box = self.navegador.find_element(By.CSS_SELECTOR, "#search input[name='q']")
        search_box.send_keys("Counter-Strike")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        # Desplazarse hacia abajo para cargar más datos
        last_height = self.navegador.execute_script("return document.body.scrollHeight")
        while True:
            self.navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.navegador.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Scraping de los datos de los últimos 30 días
        soup = BeautifulSoup(self.navegador.page_source, "html.parser")
        rows = soup.find_all("tr", class_=["even", "odd"])
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                avg_players = cols[1].text.strip()
                gain = cols[2].text.strip()
                percent_gain = cols[3].text.strip()
                peak_players = cols[4].text.strip()
                self.verbose = f"Adding... {avg_players}, {gain}, {percent_gain}, {peak_players}"
                print(self.verbose)
                data.append([avg_players, gain, percent_gain, peak_players])

        # Crear un DataFrame con los datos
        self.df = pd.DataFrame(data, columns=["Avg. Players", "Gain", "% Gain", "Peak Players"])
    def saveData(self):
        # Guardar los datos en un archivo CSV
        self.df.to_csv("steamcharts_data.csv", index=False)
        # Cerrar el navegador
        self.navegador.quit()


if __name__ == "__main__":
    steam = SteamCharts()
    steam.scrap()

