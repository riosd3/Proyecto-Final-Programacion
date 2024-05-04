from os.path import join, dirname, abspath
from os import getcwd

# Handling
cwd = getcwd()
pages_file_dir = dirname(abspath(__file__))
pages_json = join(pages_file_dir, "pages.json")
# Modify - here we should put all absolute paths or directories for the images we would use in our Tkinter window :)

