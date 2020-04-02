from typing import List
import pageshot
from PIL import Image

from playtest_cards.dimensions import Dimension
from playtest_cards.utils import SequentialFilename

_screenshoter = None


def get_screenshoter(dimensions: Dimension):
    if _screenshoter is None:
        return pageshot.Screenshoter(
            width=dimensions.dimensions[0], height=dimensions.dimensions[1]
        )
    return _screenshoter


def generate_screenshot(html_file, output_image_name, dimensions: Dimension,
use_imgkit=False) -> str:
    if use_imgkit:
        import imgkit
        imgkit.from_file(html_file, output_image_name)
    else:
        get_screenshoter(dimensions).take_screenshot(
            "file://" + html_file, output_image_name
        )
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
    new_im = Image.new("RGB", size=dimensions.total_size, color=(255, 255, 255, 0))
    joined_img_name = next(output_name_iter)
    all_filename.append(joined_img_name)

    for i, img_file in enumerate(img_array):
        im = Image.open(img_file)
        if not dimensions.potrait:
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
