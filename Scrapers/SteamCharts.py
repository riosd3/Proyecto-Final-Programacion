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
from requests import get
class SteamCharts():
    data = {"name":[],
            "current_players":[],
            "30-day_average":[],
            "30-day_gain":[],
            "30-day_percent_gain":[]
            }
    def __init__(self):
        # Configuración del navegador
        if not pagesAvailability["steamcharts"]["filtered"]:
            self.main_url = pagesAvailability["steamcharts"]["main_url"]
            #s = Service(ChromeDriverManager().install())
            #options = Options()
            #options.add_argument('--ignore-certificate-errors')
            #options.add_argument('--ignore-ssl-errors')
            #options.add_argument("--window-size=1020,1200")
            #options.add_argument("--headless")
            #self.navegador = webdriver.Chrome(service=s, options=options)
            self.inst_status = True
        else:
            self.inst_status = False

    def scrap(self, gamename):
        # Navegación a la página SteamCharts
        gamename = gamename.replace(" ", "+")
        url = f"{self.main_url}/search/?q=" + gamename
        r = get(url)
        try:
            table = BeautifulSoup(r.content.decode(), "html5lib").find("table", {"class":"common-table"}).find("tbody").find("tr")
        except Exception as e:
            print(e)
        else:
            vl = []
            for value_tags in table.find_all("td")[1:]:
                vl.append(value_tags.get_text())
            """
            self.data["name"].append(vl[0].strip())
            self.data["current_players"].append(vl[1])
            self.data["30-day_average"].append(vl[2])
            self.data["30-day_gain"].append(vl[3])
            self.data["30-day_percent_gain"].append(vl[4])
            return self.data
            """
            return vl


    def saveData(self):
        # Guardar los datos en un archivo CSV
        self.df.to_csv("steamcharts_data.csv", index=False)
        # Cerrar el navegador
        self.navegador.quit()


if __name__ == "__main__":
    steam = SteamCharts()
    r = steam.scrap(gamename="Fallout 4")
    print(r)

