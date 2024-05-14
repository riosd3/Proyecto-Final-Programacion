from os import getcwd
from os.path import join
from time import sleep
from tkinter import *
from tkinter.messagebox import askyesno, showerror, showinfo
from tkinter.ttk import Progressbar
from mainSettings import random_image_path
from sys import path
path.append("Scrapers")
from threading import Thread


class ScraperUserInterface:
    def __init__(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.scraper_gui_exit)
        self.root.title("Little Gaming Geek")
        self.icon = random_image_path("Iconos")
        self.root.iconbitmap(self.icon)
        self.root.geometry("900x650")
        self.root.resizable(0, 0)
        self.root.after(20, self.load_init)
        self.root.mainloop()

    def import_scrapers(self):
        from Scrapers.MetaCritic import MetaCritic
        self.loading_bar["value"] += 1
        from Scrapers.PriceCharting import PriceCharting
        self.loading_bar["value"] += 1
        from Scrapers.PriceGrabber import PriceGrabber
        self.loading_bar["value"] += 1
        self.scrapers = []
        for scraper_init in [MetaCritic, PriceCharting, PriceGrabber]:
            try:
                self.scrapers.append(scraper_init())
            except:
                continue
        for scraper in self.scrapers:
            if scraper.inst_status:
                print("Available: ", scraper)
        self.load_main()
    #def load_scraper_interface(self, scraper_name):
    #    if scraper_name.lower() in ["metacritic", "pricecharting", "pricegrabber", "steamcharts"] : {"metacritic":self.load_metacritic, "pricecharting":self.load_pricecharting, "pricegrabber":self.load_pricegrabber, "steamcharts":self.load_steamcharts}[scraper_name.lower()]()
    def update_meta_message(self):
        meta = self.scraperObject("metacritic")
        last = 0
        while True:
            sleep(0.2)
            try:
                last = meta.scraper_counter
            except:
                pass
            else:
                break
        while True:
            sleep(0.2)
            try:
                if meta.scraper_counter != last:
                    self.informative_text_box.insert(END, meta.info_message)
                    last = meta.scraper_counter
            except:
                pass
            else:
                self.informative_text_box.yview_moveto(1.0)
    def load_metacritic(self):
        print("Loading metacritic...")
        self.root.geometry("900x600")
        def gen_filter_url():
            scraper_filters = self.scraperObject("metacritic").getFilters()
            formed_url = {}
            for filter_name, filters_info in scraper_filters.items():
                formed_url.update({filter_name:[]})
                for info in filters_info:
                    if info["checkbutton_state"].get(): # this is a IntVar object from tkinter
                        formed_url[filter_name].append(info)
            if all(list(formed_url.values())):
                meta = self.scraperObject("metacritic")
                #meta.scrap(filters=formed_url, )
        def checkbuttons(category, clear = False):
            scraper_filters = self.scraperObject("metacritic").getFilters()
            print(scraper_filters)
            for info in scraper_filters[category]:
                meta = self.scraperObject("metacritic")
                try:
                    if clear:
                        meta.filters[category][meta.filters[category].index(info)]["checkbutton_state"].set(0)
                    else:
                        meta.filters[category][meta.filters[category].index(info)]["checkbutton_state"].set(1)
                except:
                    print("Something fails at setting checkbutton", info)
        def verify_results():
            scraper_filters = self.scraperObject("metacritic").getFilters()
            filters_selected = {}
            for filter_name, filters_info in scraper_filters.items():
                filters_selected.update({filter_name: []})
                for info in filters_info:
                    if info["checkbutton_state"].get():
                        filters_selected[filter_name].append(info)
            tmp = filters_selected.copy()
            filters_selected.pop("Release Type")
            if not self.min_year_filter_value.get().strip() and not self.max_year_filter_value.get().strip():
                self.min_year_filter_value.set(self.min_max_year[0])
                self.max_year_filter_value.set(self.min_max_year[1])
            try:
                int(self.min_year_filter_value.get().strip())
                int(self.max_year_filter_value.get().strip())
            except:
                showerror("Error filtro de fecha", "Debes ingresar informacion valida en los filtros de fecha")
            meta = self.scraperObject("metacritic")
            max_pages_found = meta.scrap(filters=tmp, date_range=(int(self.min_year_filter_value.get()), int(self.max_year_filter_value.get())), verify = True)
            if not max_pages_found:
                showerror("Sin resultados", "No se han encontrado resutlados para estos filtros")
            else:
                r = askyesno("Resultados", f"Se han encontrado {max_pages_found} resultados\nDeseas escrapearlos? ._.")
                if r:
                    informational_message = Thread(target = self.update_meta_message)
                    informational_message.start()
                    scrap_lambda = lambda: meta.scrap(filters=tmp, date_range=(int(self.min_year_filter_value.get()), int(self.max_year_filter_value.get())),limit_pages=max_pages_found)
                    scrap_thread = Thread(target=scrap_lambda)
                    scrap_thread.start()
                    #meta.scrap(filters=tmp, date_range=(int(self.min_year_filter_value.get()), int(self.max_year_filter_value.get())), limit_pages=max_pages_found)
        def save_scraped():
            meta = self.scraperObject("metacritic")
            meta.save_data()



        self.meta_header_frame = Frame(self.header_frame)
        #self.meta_header_frame.pack()
        self.meta_body_frame = Frame(self.body_frame)
        #self.meta_body_frame.pack()
        self.meta_footer_frame = Frame(self.footer_frame)
        #self.meta_footer_frame.pack()

        ##########################################################################
        # Honestamente Chatgepeteado:)
        self.scraper_title = Label(self.meta_header_frame, text="MetaCritic scraper", font = ("Arial", 14, "bold"), fg = "#FFCC33")
        self.scraper_title.grid()

        # Frame that holds all the category buttons and their frames
        inner_frame = Frame(self.meta_body_frame)
        inner_frame.grid(row=1, column=0, sticky='ew')

        #self.toggle_buttons = {}
        c = 0  # Column counter for the main buttons

        scraper = self.scraperObject("metacritic")
        if scraper:
            filters = scraper.getFilters()

            for toggle_button_name, filters_info in filters.copy().items():
                filter_label = Label(inner_frame, text=toggle_button_name.capitalize(), font = ("Arial", 10, "bold"), fg = "black")#, command=lambda toggle_button_name=toggle_button_name: toggle_filters(toggle_button_name.lower()))
                filter_label.grid(row=0, column=c, sticky = "ew")

                # Scrollable frame setup for each category without causing unnecessary expansion
                scroll_frame = Frame(inner_frame)
                scroll_frame.grid(row=1, column=c, sticky = "nwes")

                # Canvas and vertical scrollbar within each scroll_frame
                canvas = Canvas(scroll_frame, width=200, height=200)  # Define a fixed size for canvas to prevent expansion
                v_scrollbar = Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=v_scrollbar.set)

                # Frame that holds the checkbuttons, this is placed inside the canvas
                checkbutton_frame = Frame(canvas)
                canvas.create_window((0, 0), window=checkbutton_frame, anchor='nw')#, width=200, height=200)

                # Pack everything in the scroll_frame
                canvas.pack(side="left", fill="both")
                v_scrollbar.pack(side="right", fill="y")

                # Bind to adjust the scroll region automatically
                checkbutton_frame.bind("<Configure>", lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

                #self.toggle_buttons[toggle_button_name.lower()] = {"button": button, "frame": checkbutton_frame}

                if toggle_button_name.lower() in ["platforms", "genre", "release type"]:
                    for info in filters_info:
                        var = IntVar()
                        #print(filters[toggle_button_name][c], "test")
                        filters[toggle_button_name][filters[toggle_button_name].index(info)].update({"checkbutton_state":var}) # .copy in the for to not have any errors here:)
                        #print("Hey, I am the same look ---> ", id(var), " == ", id(filters[toggle_button_name][filters[toggle_button_name].index(info)]["checkbutton_state"]))
                        ck_button = Checkbutton(checkbutton_frame, text=info["name"], variable = var)
                        ck_button.pack(anchor='w')

                c += 1  # Increment column index for the next set of filter category
            #self.clear_buttons_frame = Frame(inner_frame)
            #self.clear_buttons_frame.grid()
            frame_platforms_buttons = Frame(inner_frame)
            frame_platforms_buttons.grid(row=2, column=0)
            self.clear_platforms_checkbuttons = Button(frame_platforms_buttons, text="Deseleccionar todo", command=lambda: checkbuttons("Platforms", clear=True))
            self.clear_platforms_checkbuttons.grid(row=0, column=0, sticky="we")
            self.select_platforms_checkbuttons = Button(frame_platforms_buttons, text="Seleccionar todo", command=lambda: checkbuttons("Platforms", clear=False))
            self.select_platforms_checkbuttons.grid(row=0, column=1, sticky="we")

            frame_release_type_buttons = Frame(inner_frame)
            frame_release_type_buttons.grid(row=2, column=1)
            self.clear_release_type_checkbuttons = Button(frame_release_type_buttons, text="Deseleccionar todo", command=lambda: checkbuttons("Release Type", clear=True))
            self.clear_release_type_checkbuttons.grid(row=0, column=0, sticky="we")
            self.select_release_type_checkbuttons = Button(frame_release_type_buttons, text="Seleccionar todo", command=lambda: checkbuttons("Release Type", clear=False))
            self.select_release_type_checkbuttons.grid(row=0, column=1, sticky="we")

            frame_genre_checkbuttons = Frame(inner_frame)
            frame_genre_checkbuttons.grid(row=2, column=2)
            self.clear_genre_checkbuttons = Button(frame_genre_checkbuttons, text="Deseleccionar todo", command=lambda: checkbuttons("Genre", clear=True))
            self.clear_genre_checkbuttons.grid(row=0, column=0)
            self.select_genre_checkbuttons = Button(frame_genre_checkbuttons, text="Seleccionar todo", command=lambda: checkbuttons("Genre", clear=False))
            self.select_genre_checkbuttons.grid(row=0, column=1)

        self.min_max_year = self.scraperObject("metacritic").getYearFilter()
        frame_minmax_year = Frame(self.meta_body_frame)
        frame_minmax_year.grid(row = 3, column = 0, sticky = "w")
        self.max_year_filter_value = StringVar()
        self.min_year_filter_value = StringVar()
        max_year_filter = Entry(frame_minmax_year, textvariable=self.max_year_filter_value)
        min_year_filter = Entry(frame_minmax_year, textvariable=self.min_year_filter_value)
        max_year_filter.grid(row = 1, column = 1, sticky = "e")
        min_year_filter.grid(row = 1, column = 0, sticky = "w")
        label_max_year = Label(frame_minmax_year, text = f"Min year: {self.min_max_year[0]}")
        label_max_year.grid(row = 0, column = 0)
        label_min_year = Label(frame_minmax_year, text = f"Max year: {self.min_max_year[1]}")
        label_min_year.grid(row = 0, column = 1)


        scrap_related_frame = Frame(self.meta_body_frame)
        scrap_related_frame.grid(row = 4, column = 0, sticky = "e")
        self.save_scraped = Button(scrap_related_frame, text = "Guardar", command = save_scraped)
        self.save_scraped.grid(row = 0, column = 0)
        self.verify_params_button = Button(scrap_related_frame, text="Verificar resultados", command = verify_results)
        self.verify_params_button.grid(row=0, column=1)
        self.scrap_button = Button(scrap_related_frame, text = "Scrap", command = gen_filter_url, bg = "green", fg = "white", font = ("Arial", 10, "bold"))
        self.scrap_button.grid(row = 0, column = 2)
        self.informative_text_box = Text(self.meta_footer_frame, wrap = WORD)
        self.informative_text_box.pack(fill = "both", expand = True)
        temp = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠟⠋⠙⠋⠉⠙⢷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣶⣶⣄⠀⠀⠀⢠⣾⣿⣁⡀⠀⠀⠀⠀⠀⠀⢑⣿⡆⠀⠀⠀⢠⣾⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣾⣦⡀⢠⣾⡿⣛⣛⡻⢷⣄⠀⠀⣴⣾⣿⠛⠻⠦⣄⣴⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠻⢿⣿⣿⣿⣿⣿⢿⣿⣿⣧⢼⣿⣿⣿⠿⣿⣇⢸⡟⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠿⢿⣾⣿⣤⠿⠋⠀⠈⠻⢿⣿⣧⣿⠟⣬⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠃⠀⠀⢀⣴⣖⣶⠀⠀⠀⠀⠀⢀⡈⠀⠀⢘⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣶⣶⣶⠿⠿⠿⠿⠷⠶⠶⠶⠛⠋⠻⣦⣤⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡇⠀⣿⠻⢷⣤⣀⠀⠀⠀⠈⠀⠀⠀⣀⣈⡻⢿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⡿⠛⡏⠁⠂⠘⠭⢿⣒⣒⡒⠒⠒⠊⠉⠁⠀⠀⣿⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠟⠁⡄⠣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡌⠙⠲⣤⣀⠠⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣏⠀⠀⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠋⠀⠀⠀⠀⠈⠙⠚⠓⠶⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣶⣀⡴⠛⢷⣄⣠⣄⡀⠀⠀⠀⠀⠀⠀⠀⠐⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠳⢦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⠴⠾⣿⣿⣿⣿⣿⠟⠛⠿⣿⣦⣄⠙⢻⣿⣷⣦⡤⠤⠶⠒⠛⠁⣠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⡾⠏⠁⠀⠀⠀⠀⠰⠿⠟⠋⠀⠀⠀⠀⠈⠉⠛⠙⠋⠉⠉⠀⠀⠀⠀⠀⣀⡴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢉⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀
⠀⠀⠀⠀⢄⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢸⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣧⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀
⠀⠀⠀⠀⣼⣋⣧⣶⠀⠀⠀⢀⡀⣀⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⣼⣿⣿⣟⣤⡀⠀⠀⠀⠀⠀⠀⠘⣦⠀⠀
⠀⠀⠀⠀⣿⡟⡇⣿⣤⣤⣴⣼⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⣷⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠏⣴⣿⣿⠋⠉⠉⠛⠋⡄⠂⠀⠀⠀⠀⠈⣇⠀
⠀⠀⠀⢀⣿⣷⣜⢿⣿⣿⣿⣿⣿⣿⣟⢿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⠾⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠐⠖⣠⣶⣿⣟⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀
⠀⠀⢀⣾⠋⠻⣿⡶⠍⠙⠛⢿⣿⣿⣿⣮⡙⠿⣿⣶⣤⣄⣀⣤⣤⣤⣤⡀⢀⣈⣁⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⣾⠇⠀⠀⠘⢷⡇⠀⠀⠀⢿⣿⣿⣿⣿⣶⣼⣿⣿⣟⣻⣿⣿⣿⣿⡿⠟⠛⠁⠀⠉⠻⢿⣿⣶⣤⣴⣶⣶⣤⣶⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠇
⠀⢸⣿⠀⠀⠀⢠⡞⠀⠀⠀⠀⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣋⣠⣀⠀⠀⠀⠀⠀⠀⠀⢉⣛⢻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠀
⠀⢸⡏⠀⠀⠀⣼⠁⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠿⡿⠛⠉⠉⠉⠁⠀⢀⠀⠀⠀⠀⠀⠉⠰⠿⠿⠛⠻⠟⠉⠁⢩⢹⣿⣿⣄⠀⠸⣆⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀
⠀⣿⢿⠀⠀⣰⠇⠀⠀⠀⠀⠀⣿⡟⢻⣿⣿⣿⣿⣿⡟⠻⢶⣤⠀⠀⠀⠀⠀⠀⠀⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢿⣿⣿⣦⠀⢹⣆⠀⠀⠀⠀⠀⠀⠀⡇⠀
⢀⡟⠺⠀⢐⡿⠀⠀⠀⠀⢀⣼⣿⠁⠀⢻⣿⣿⣿⣿⣿⣷⣤⣿⣤⣤⣤⣤⣶⡄⠀⠀⣿⣇⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀⠈⢿⣷⣿⡾⠁⢿⣿⣷⣿⣿⡷⠀⠀⠀⠀⠀⠀⡇⠀
⢸⡇⠀⠘⣿⡁⠀⠀⢀⣰⣿⣿⠃⠀⠀⠀⢻⣿⣽⠋⠛⢯⢿⣿⠛⠛⠋⠉⠙⠛⠲⣄⠉⠉⠁⠈⠉⠙⠛⠷⣦⣤⣤⣌⠀⠀⢸⡟⠁⠀⠀⠻⣿⣿⣿⣍⠀⠀⠀⠀⠀⠀⢧⠀
⢸⠁⠀⠀⢹⣷⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⢸⣿⢢⠀⠂⠀⣭⣿⡀⠀⠀⠀⠀⠀⠀⢸⡉⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⡿⠀⠀⠀⠀⠀⢹⣿⡿⠉⠀⠀⠀⠀⠀⠀⡾⠀
⠀⠀⠀⠀⠀⠋⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⣼⣏⠈⠁⢰⠀⢨⣿⣧⣀⡀⣠⠀⠀⠀⣸⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⠀⠀⠀⣸⡍⠁⠀⠀⠀⠀⠀⠀⣠⣷⠀
⠀⠀⠀⠀⠀⠀⠙⢿⣿⡇⠀⠀⠀⠀⠀⢠⣿⠟⠇⠀⠈⠑⢦⣿⠿⠿⠿⠿⠶⢀⢀⣸⠿⣶⣦⣠⡖⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠘⢻⡆
⠀⠀⠀⠀⠀⠀⠀⠀⣼⡇⠀⠀⠀⠀⠀⣸⡗⠀⠀⠀⠀⠀⠀⠙⠷⡄⣀⠀⠀⠻⠟⠃⠀⠀⠀⠀⠤⠀⠀⠀⠀⠀⠀⠀⣾⡟⠀⠀⠀⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠹⠇⠀⠀⠀⠀⠀⣸⣿⠠⢰⣶⠄⠀⠀⠀⢀⣀⠀⢠⠀⠀⢠⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣙⣿⠁⠀⠀⠀⠀⠀⣸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠇"""
        self.informative_text_box.insert(END, temp)

    def load_pricecharting(self):
        print("Loading pricecharting...")
        ############
        self.pricecharting_header_frame = Frame(self.main_frame)
        #self.pricecharting_header_frame.pack()
        self.pricecharting_body_frame = Frame(self.main_frame)
        #self.pricecharting_body_frame.pack()
        self.pricecharting_footer_frame = Frame(self.main_frame)
        #self.pricecharting_footer_frame.pack()
        ############
        button = Button(self.pricecharting_footer_frame, text = "This is a test")
        button.grid()
    def switch_scraper_interface(self, scraper_name):
        meta_frames = [self.meta_header_frame, self.meta_body_frame, self.meta_footer_frame]
        pricecharting_frames = [self.pricecharting_header_frame, self.pricecharting_body_frame, self.pricecharting_footer_frame]
        # CPP templates equivalent????
        try:
            for frame in meta_frames:
                frame.pack_forget()
        except:
            pass
        try:
            for frame in pricecharting_frames:
                frame.pack_forget()
        except:
            pass
        try:
            self.header.pack_forget()
        except:
            print("Could not unpack load_main main")
        try:
            self.body.pack_forget()
        except:
            print("Could not unpack load_main body")
        if "metacritic" == scraper_name:
            try:
                for frame in meta_frames:
                    frame.pack()
            except:
                pass
        elif "pricecharting" == scraper_name:
            try:
                for frame in pricecharting_frames:
                    frame.pack()
            except:
                pass
    def load_pricegrabber(self):
        print("Loading pricegrabber...")
    def load_steamcharts(self):
        print("Loading steamcharts")
    def scraper_gui_exit(self):
        # if there are cached data must be modify the message informing that
        r = askyesno("Salir", "Estas seguro que deseas salir del programa?")
        if r:
            self.root.destroy()
    def scraperObject(self, scraper_name):
        for scraper in self.scrapers:
            if (type(scraper).__name__).lower() == scraper_name:
                return scraper
        return False
    def load_main(self):
        # this is loaded when not scraper is selected
        self.loading_frame.destroy()
        self.root.geometry("900x650")
        self.main_frame = Frame(self.root)
        self.main_frame.pack()
        # Main header
        self.header_frame = Frame(self.main_frame)
        self.header_frame.pack()
        self.header = Label(self.header_frame, text = "Chose a scraper to start!")
        self.header.pack()
        self.menu = Menu(self.root)
        self.menu_scrapers = Menu(self.main_frame, tearoff=0)
        for available_scraper in self.scrapers:
            scraper_name = type(available_scraper).__name__
            self.menu_scrapers.add_command(label=scraper_name,command=lambda scraper_name=scraper_name: self.switch_scraper_interface(scraper_name.lower())) # scraper_name=scraper_name is like localthread variable in cpp to not have the last for every button
        #self.menu_scrapers.add_command(label = "MetaCritic")
        self.menu_scrapers.add_separator()
        self.menu_scrapers.add_command(label = "Salir", command = self.scraper_gui_exit)
        self.menu.add_cascade(label = "Scrapers", menu = self.menu_scrapers)
        self.root.config(menu = self.menu)
        # Main body
        self.body_frame = Frame(self.main_frame)
        self.body_frame.pack()
        self.body = Label(self.body_frame)
        self.body.pack()
        # Main footer
        self.footer_frame = Label(self.main_frame)
        self.footer_frame.pack()
        self.init_every_scraper_interface_thread = Thread(target = self.init_every_scraper_interface)
        self.init_every_scraper_interface_thread.start()
    def init_every_scraper_interface(self):
        self.load_steamcharts()
        self.load_pricecharting()
        self.load_metacritic()
    def load_init(self):
        self.loading_frame = Frame(self.root)
        self.loading_frame.pack()
        self.img = random_image_path("FondosInicio")
        self.img_obj = PhotoImage(file = self.img)
        self.background_loading = Label(self.loading_frame, image = self.img_obj)
        self.background_loading.pack(fill = "both", expand = True)
        self.loading_message = Label(self.loading_frame, text = "[[ Cargando scrapers ]]", font = ('Arial', 15, 'bold'), fg = 'black' )#, padx = 40, pady = 40)
        self.loading_message.pack(side = "top")
        self.length_loading_bar = 3
        self.loading_bar = Progressbar(self.loading_frame, orient = "horizontal", mode = "determinate", length = 100, maximum = self.length_loading_bar)
        self.loading_bar.pack(fill = "both", expand = True)
        self.loading_bar["value"] = 0
        self.root.geometry(f"{self.img_obj.width() + 50}x{self.img_obj.height() + 50}")
        # this avoid freeze the GUI, thats the whole idea of the loading page:p
        self.import_thread = Thread(target=self.import_scrapers)
        self.import_thread.start()

class MetaCriticInterface:
    pass

if __name__ == "__main__":
    a = ScraperUserInterface()