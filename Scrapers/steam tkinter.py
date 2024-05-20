import json
import time
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import imageio
from PIL import Image, ImageTk


with open('C:/Users/Alexb/OneDrive/Escritorio/tarea/pages.json') as json_file:
    pagesAvailability = json.load(json_file)

class SteamCharts():
    def __init__(self, status_label, game_name):
        self.status_label = status_label
        self.game_name = game_name
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
        self.update_status(f"Iniciando scraping para {self.game_name}...")
        try:
            self.navegador.get(self.main_url)
            time.sleep(5)

            search_box = self.navegador.find_element(By.CSS_SELECTOR, "#search input[name='q']")
            search_box.send_keys(self.game_name)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            last_height = self.navegador.execute_script("return document.body.scrollHeight")
            while True:
                self.navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = self.navegador.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

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
                    data.append([avg_players, gain, percent_gain, peak_players])

            self.df = pd.DataFrame(data, columns=["Avg. Players", "Gain", "% Gain", "Peak Players"])
            self.update_status("Scraping completado.")
        except Exception as e:
            self.update_status(f"Error durante el scraping: {str(e)}")
        finally:
            self.navegador.quit()

    def save_data(self):
        if hasattr(self, 'df'):
            filename = f"{self.game_name}_steamcharts_data.csv"
            self.df.to_csv(filename, index=False)
            self.update_status(f"Datos guardados en {filename}")
        else:
            self.update_status("No hay datos para guardar.")

    def update_status(self, message):
        self.status_label.config(text=message)
        self.status_label.update()

class SteamChartsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SteamCharts Scraper")
        self.geometry("400x300")
        self.resizable(False, False)  # Deshabilitar la capacidad de redimensionar la ventana

        self.status_label = tk.Label(self, text="Estado: Esperando", wraplength=300)
        self.status_label.pack(pady=10)

        self.game_entry_label = tk.Label(self, text="Ingrese el nombre del juego:")
        self.game_entry_label.pack(pady=5)

        self.game_entry = tk.Entry(self)
        self.game_entry.pack(pady=5)

        self.scrap_button = tk.Button(self, text="Iniciar Scraping", command=self.start_scraping)
        self.scrap_button.pack(pady=5)

        self.save_button = tk.Button(self, text="Guardar Datos", command=self.save_data)
        self.save_button.pack(pady=5)

        # Agregar etiqueta para mostrar el GIF
        self.gif_label = tk.Label(self)
        self.gif_label.pack(pady=10)

        # Cargar y mostrar el GIF
        self.load_gif("C:/Users/Alexb/OneDrive/Escritorio/tarea/groove-battle.gif")

    def load_gif(self, gif_path):
        self.gif_frames = []
        self.gif = imageio.mimread(gif_path)
        for frame in self.gif:
            img = Image.fromarray(frame)
            self.gif_frames.append(ImageTk.PhotoImage(img))
        self.gif_index = 0
        self.update_gif()

    def update_gif(self):
        frame = self.gif_frames[self.gif_index]
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.gif_label.config(image=frame)
        self.after(100, self.update_gif)

    def start_scraping(self):
        game_name = self.game_entry.get()
        if game_name:
            self.scraper = SteamCharts(self.status_label, game_name)
            if self.scraper.inst_status:
                self.scraper.scrap()
            else:
                self.status_label.config(text="Página no disponible para scraping.")
        else:
            self.status_label.config(text="Por favor, ingrese el nombre de un juego.")

    def save_data(self):
        if hasattr(self, 'scraper'):
            self.scraper.save_data()
        else:
            self.status_label.config(text="Primero inicie el scraping.")

if __name__ == "__main__":
    app = SteamChartsApp()
    app.mainloop()
