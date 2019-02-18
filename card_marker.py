#!/usr/bin/env python
from PIL import Image
import click
import pageshot

# based on 9*6 requirements for 4096 * 4096
DIMENSION = (455, 682)
IMAGES_LAYOUT = (9, 6)
TOTAL_IMAGES = IMAGES_LAYOUT[0] * IMAGES_LAYOUT[1]
NEW_IMAGE_SIZE = (
    DIMENSION[0]*IMAGES_LAYOUT[0],
    DIMENSION[1]*IMAGES_LAYOUT[1]
)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-t', '--template', type=click.STRING)
@click.option('-o', '--output', type=click.STRING, default='out.png')
def render(template, output):
    """Given a folder, render the image generated for boardgame simulator
    """
    print("Rendering: {}".format(template))
    # Render html into png
    tmp_img_file = 'output.1.png'
    url = "file:///Users/borislau/personal/card_maker/example_game/layout.html"
    s = pageshot.Screenshoter(width=DIMENSION[0], height=DIMENSION[1])

    s.take_screenshot(url, tmp_img_file)

    # layout png in sequential format
    join_images([tmp_img_file] * TOTAL_IMAGES, output)
    print("Output: {}".format(output))


def join_images(img_array, joined_img):
    assert len(img_array) <= TOTAL_IMAGES, "Cannot paste too mange images"
    # creates a new empty image, RGB mode, and size 400 by 400.
    new_im = Image.new('RGB',
                       size=NEW_IMAGE_SIZE, color=(255, 255, 255, 0))

    for i, img_file in enumerate(img_array):
        im = Image.open(img_file)
        resized_im = im.resize(DIMENSION, Image.ANTIALIAS)
        x = (i % IMAGES_LAYOUT[0]) * DIMENSION[0]
        y = i // IMAGES_LAYOUT[0] * DIMENSION[1]
        new_im.paste(resized_im, (x, y))

    new_im.save(joined_img)


if __name__ == "__main__":
    cli()
