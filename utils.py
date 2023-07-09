import os


image_extions = ('.JPG', '.JPEG', '.PNG', '.TIFF', '.BMP')

def is_image_file(filepath):
    if not os.path.isfile(filepath):
        return False
    _, ext = os.path.splitext(filepath)
    if ext: ext = ext.upper()
    else: return False
    if ext in image_extions:
        return True
    else:
        return False