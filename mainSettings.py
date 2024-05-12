from os.path import join, abspath
from os import getcwd, listdir
from random import choice

cwd = getcwd()
images_directory = join(cwd, "images")
# Color for the root background window
root_bg_color = "#41B921"
def random_image_path(image_from):
    if image_from in listdir(images_directory):
        images_from_this_dir = join(images_directory, image_from)
        return join(images_from_this_dir, choice(listdir(images_from_this_dir)))
    else:
        print(f"There is not directory for images: {image_from} in {images_directory}")