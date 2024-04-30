from os.path import join
from os import getcwd
# Modify - here we should put all absolute paths or directories for the images we would use in our Tkinter window :)
file_with_pages = "pages.json"


# Handling
cwd = getcwd()
pages_json = join(cwd, file_with_pages)