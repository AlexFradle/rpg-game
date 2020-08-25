from PIL import Image
from os import listdir, mkdir
from os.path import isfile, join, isdir
from psd_tools import PSDImage
from os import rename


# def convert_images(prefix, folder_name, num_of_images):
#     nums = [str(i) if i > 9 else "0" + str(i) for i in range(1, num_of_images)]
#
#     for num in nums:
#         file_name = f"{prefix}_{num}"
#         im = PSDImage.open(f"C:/Users/Alw/Downloads/flatskillsicons_windows/flatskillsicons/{folder_name}/{file_name}.PSD")
#         file = im.composite()
#         file.save(f"C:/Users/Alw/Downloads/flatskillsicons_windows/flatskillsicons/{folder_name}/{file_name}.png")
#         print(f"Saved: {file_name}.png")


def item_drop_resize(path_from, path_to, width, height):
    files = [f for f in listdir(path_from) if isfile(join(path_from, f))]
    print(files)

    if not isdir(path_to):
        mkdir(path_to)

    for file in files:
        im = Image.open(path_from + file)
        resized = im.resize((width, height))
        new_name = file[:-4] + "_drop.png"
        resized.save(path_to + new_name)
        print(f"Saved {new_name}")


def animation_rename(path: str, prefix: str):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        rename(path + file, f"{path}{prefix}_{file}")


# item_drop_resize(
#     "C:/Users/Alw/Desktop/rpg_game/assets/items/",
#     "C:/Users/Alw/Desktop/rpg_game/assets/item_drops/",
#     20, 20
# )

animation_rename("C:/Users/Alw/Desktop/rpg_game/assets/animation/diamond/", "diamond")
