#!/usr/bin/env python
import os

import yaml
import click
import jinja2
import pageshot
from PIL import Image

# based on 9*6 requirements for 4096 * 4096
DIMENSION = (455, 682)
IMAGES_LAYOUT = (9, 6)
TOTAL_IMAGES = IMAGES_LAYOUT[0] * IMAGES_LAYOUT[1]
NEW_IMAGE_SIZE = (
    DIMENSION[0]*IMAGES_LAYOUT[0],
    DIMENSION[1]*IMAGES_LAYOUT[1]
)

TMPFILE_FOLDER = os.path.abspath('genfile')

_screenshoter = None


def get_screenshoter():
    if _screenshoter is None:
        return pageshot.Screenshoter(width=DIMENSION[0], height=DIMENSION[1])
    return _screenshoter


@click.group()
def cli():
    pass


@cli.command()
@click.argument('content_yaml')
@click.option('-o', '--output', type=click.STRING, default='out.png')
def render(content_yaml, output):
    """Given a folder, render the image generated for boardgame simulator
    """
    image_files = parse_content(content_yaml)

    # layout png in sequential format
    join_images(image_files, output)
    print("Output: {}".format(output))


def parse_content(content_file):
    output_images = []
    content_path = os.path.dirname(os.path.abspath(content_file))

    with open(content_file, 'r') as stream:
        data = yaml.load_all(stream)
        for i, d in enumerate(data):
            if d is None:
                continue

            temp_out_img = '{tmpfolder}/output_{index}.png'.format(
                index=i, tmpfolder=TMPFILE_FOLDER
            )
            template_file = d.get('template_file')
            assert template_file, "No template file found in: {}".format(d)
            render_content(d, template_file,
                           temp_out_img, render_path=content_path)
            output_images.append(temp_out_img)
    return output_images


def render_content(data, template, tmp_img_file, render_path):
    template_abs_path = "{}/{}".format(render_path, template)
    print("Rendering: {} with data: {}".format(template_abs_path, data))

    with open(template_abs_path) as t:
        template = jinja2.Template(t.read())

    tmp_output_html = '{}/rendered.html'.format(TMPFILE_FOLDER)
    with open(tmp_output_html, 'w') as f:
        rendered_html = template.render(**data)
        f.write(rendered_html)

    get_screenshoter().take_screenshot("file://"+tmp_output_html, tmp_img_file)


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
