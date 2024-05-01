import json
from os.path import exists
from sys import exit as sys_exit
from fake_useragent import UserAgent
from requests.sessions import Session
from ScraperSettings import pages_json
class ScrapNoPages(Exception):
    def __init__(self):
        self.message = "All the pages for the scrapers are filtered"
        super().__init__(self.message)

class SpecifiedUrlFiltered(Exception):
    def __init__(self, url):
        self.url = url
        self.message = f"The url you want to access is filtered"
        super().__init__(self.message)

class FileRelatedExceptions(Exception):
    def __init__(self, file, message):
        self.file = file
        self.message = message
        super().__init__(self.message)

class NoFileForInit(FileRelatedExceptions):
    def __init__(self, file):
        super().__init__(file, "The file for initialization does not exist")

class ErrorReadingJSON(FileRelatedExceptions):
    def __init__(self, file):
        super().__init__(file, "Cannot convert JSON file into a Python dictionary")
        sys_exit(666)


class VerifyFirewall:
    useragent = UserAgent()
    s = Session()
    s.headers.update({"User-Agent":useragent.random})
    @classmethod
    def verify(cls):
        s = Session()
        # Verifica que las paginas no esten filtradas por fortinet en caso de utilizar el internet de la uni
        init_err_msg = "Error at init"
        try:
            if not exists(pages_json):
                raise NoFileForInit(pages_json)
        except NoFileForInit as e:
            print(f"{init_err_msg} : {e.message} : {e.file}")
        try:
            with open(pages_json, "r") as f:
                cls.gaming_information_web_sites = json.loads(f.read())
        except:
            raise ErrorReadingJSON(pages_json)

        def mark_filtered(web_name):
            cls.gaming_information_web_sites[web_name]["filtered"] = True
        for web_name, web_info in cls.gaming_information_web_sites.copy().items():
            for field, value in web_info.items():
                if field == "main_url":
                    try:
                        r = cls.s.get(value)
                    except:
                        mark_filtered(web_name=web_name)
                    else:
                        if r.status_code == 404 or r.status_code == 403: mark_filtered(web_name=web_name)
                    finally:
                        if r: r.close()
        validation = [i["filtered"] for i in cls.gaming_information_web_sites.copy().values()]
        try:
            if all(validation):
                raise ScrapNoPages
            else:
                print(f"Available {validation.count(False)} of {len(validation)}")
                for available, info in cls.gaming_information_web_sites.copy().items():
                    if not info["filtered"]: print(available, info["main_url"])
        except ScrapNoPages as e:
            print(f"{init_err_msg} : {e.message}")
        return cls.gaming_information_web_sites

pagesAvailability = VerifyFirewall.verify()
if __name__ == "__main__":
    r = VerifyFirewall.verify()
    print(r)