from typing import List
import os
import time
import pageshot
import atexit
from PIL import Image

from playtest_cards.dimensions import Dimension, DEFAULT_WIDTH, DEFAULT_HEIGHT
from playtest_cards.utils import SequentialFilename

from selenium import webdriver

USE_SCREENSHOTER = False
_screenshoter = None


# This is a hack to consider a more accurate browser space used.
# TODO: we need better way to account for non render space of browser
# #  (e.g.bookmark bar)
HACK_TOP_BROWSER_PADDING = 200


def get_screenshoter(dimensions: Dimension, use_screenshoter=USE_SCREENSHOTER):
    """Get screenshooter, which can be reused.

    Note that the screensize is tricky here.  That the dimensions of
    set_window_size actually only set the "browser window" size, but not
    the actual browser pixel size. (see HACK_TOP_BROWSER_PADDING)
    """
    global _screenshoter
    width = dimensions.dimensions[0]
    height = dimensions.dimensions[1] + HACK_TOP_BROWSER_PADDING
    if _screenshoter is None:
        if USE_SCREENSHOTER:
            _screenshoter = pageshot.Screenshoter(
                width=width, height=height)
        else:
            _screenshoter = webdriver.Chrome()
            _screenshoter.set_window_size(width, height)

            atexit.register(_screenshoter.quit)
    return _screenshoter


def generate_screenshot(html_file, output_image_name, dimensions: Dimension,
                        use_screenshoter=USE_SCREENSHOTER) -> str:
    file_url = "file://" + html_file
    if use_screenshoter:
        get_screenshoter(dimensions).take_screenshot(
            file_url, output_image_name)
    else:
        driver = get_screenshoter(dimensions)
        driver.get(file_url)
        time.sleep(0.5)
        driver.get_screenshot_as_file(output_image_name)
    return output_image_name


def join_images(
    img_array: List[str], output_name_iter: SequentialFilename, dimensions: Dimension
) -> List[str]:
    """Give multuple images, this function will be responsible
    for breaking down list of images into individual files

    :return: list of files output
    """
    all_filename = []

    dimension_iter = dimensions.iterate_layout()
    new_im = Image.new("RGB", size=dimensions.total_size,
                       color=(255, 255, 255, 0))
    joined_img_name = next(output_name_iter)
    all_filename.append(joined_img_name)

    for i, img_file in enumerate(img_array):
        im = Image.open(img_file)
        if not dimensions.protrait:
            im = im.rotate(90, expand=True)
        resized_im = im.resize(dimensions.dimensions, Image.ANTIALIAS)
        try:
            (x, y) = next(dimension_iter)
        except StopIteration:
            # That we have a full page.  Now start a new page
            print("Output image: {}".format(joined_img_name))
            new_im.save(joined_img_name)
            dimension_iter = dimensions.iterate_layout()
            new_im = Image.new(
                "RGB", size=dimensions.total_size, color=(255, 255, 255, 0)
            )
            joined_img_name = next(output_name_iter)
            all_filename.append(joined_img_name)
            (x, y) = next(dimension_iter)

        new_im.paste(resized_im, (x, y))

    print("Output image: {}".format(joined_img_name))
    new_im.save(joined_img_name)

    return all_filename
