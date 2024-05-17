import pandas as pd
from requests import Session
from bs4 import BeautifulSoup
from FilterCheck import pagesAvailability
from selenium import webdriver
from fake_useragent import UserAgent
class PriceCharting:
    ranWebAgent = UserAgent()
    def __init__(self):
        if not pagesAvailability["pricecharting"]["filtered"]:
            self.main_url = pagesAvailability["pricecharting"]["main_url"]
            options = webdriver.ChromeOptions()
            options.add_argument(f"--useragent={PriceCharting.ranWebAgent.random}")
            options.add_argument("--headless")
            self.browser_selenium = webdriver.Chrome(options=options)
            self.browser_requests = Session()
            self.browser_requests.headers.update({"User-Agent":PriceCharting.ranWebAgent.random})
            self.inst_status = True
        else:
            self.inst_status = False

    def getFilters(self):
        r = self.browser_requests.get(self.main_url)
        filter_tags = BeautifulSoup(r.content, "html.parser").find("ul", {"class":"menu-dropdown single"})
        filter_info = []
        for li_tags in filter_tags.find_all("li"):
            opt_result = []
            try:
                current_filtrable = BeautifulSoup(str(li_tags), "html.parser")
                title = current_filtrable.find("a", {"class":"small-desktop-hidden"}).get_text().strip().replace(" »", "")
                for opt in current_filtrable:
                    opt_filtrable = BeautifulSoup(str(opt), "html.parser")
                    try:
                        # This get the names from the menu
                        console_name = opt_filtrable.find("a", {"class":"small-desktop-hidden"}).get_text().strip()
                    except:
                        print("Something fails at getFilters for PriceCharting we can not get category name")
                    else:
                        try:
                            # Zero in the list to erase Japan and PAL (Europe)
                            console_names_and_tags = BeautifulSoup(str(opt_filtrable.find_all("ul")[0]), "html.parser")
                        except:
                            print("Can find consoles for category: ", console_name)
                        else:
                            for li_console_info in console_names_and_tags.find_all("a"):
                                try:
                                    console_name = li_console_info.get_text().strip()
                                    href = li_console_info.get("href")
                                except:
                                    print("Cant find console name and href for: ", console_name)
                                else:
                                    opt_result.append({"console_name":console_name, "href":href})
                    print(opt_result)
            except:
                pass
            else:
                filter_info.append({"console_category":title, "filter_info":opt_result})
        return filter_info





if __name__ == "__main__":
    pricechar = PriceCharting()
    print(pricechar.inst_status)
    if pricechar.inst_status:
        filters = pricechar.getFilters()
        print(filters)
