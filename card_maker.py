#!/usr/bin/env python
import os

import yaml
import click
import jinja2
import pageshot
from PIL import Image

from libcardmaker.dimensions import LAYOUT
from libcardmaker.sheets import SheetReader


TMPFILE_FOLDER = os.path.abspath('genfile')

_screenshoter = None


def get_screenshoter(dimensions):
    if _screenshoter is None:
        return pageshot.Screenshoter(
            width=dimensions.dimensions[0], height=dimensions.dimensions[1])
    return _screenshoter


@click.group()
def cli():
    pass


@cli.command()
@click.argument('content_sheet')
@click.option('-s', '--sheetname', type=click.STRING, default='Sheet1')
@click.option('-o', '--output', type=click.STRING, default='out')
@click.option('-l', '--layout', type=click.STRING, default='paper')
def render(content_sheet, output, layout, sheetname):
    """Given a folder, render the image generated for boardgame simulator
    """
    # layout png in sequential format
    dimensions = LAYOUT[layout]
    image_files = parse_content(
        content_sheet, sheetname, dimensions=dimensions)
    join_images(image_files, output, dimensions=dimensions)


def parse_content(content_sheet, sheet_name, dimensions):
    output_images = []

    for i, d in enumerate(iter(
            SheetReader(content_sheet, sheet_name=sheet_name
                        ))):
        print("Getting data: {}".format(d))
        temp_out_img = '{tmpfolder}/output_{index}.png'.format(
            index=i, tmpfolder=TMPFILE_FOLDER
        )
        template_file = d.get('template_file')
        assert template_file, "No template file found in: {}".format(d)
        render_content(d, template_file,
                       temp_out_img, render_path=os.getcwd(),
                       dimensions=dimensions)
        count = int(d.get('count', 1))
        output_images.extend([temp_out_img] * count)
    return output_images


def render_content(data, template, tmp_img_file, render_path, dimensions):
    template_abs_path = "{}/{}".format(render_path, template)
    print("Rendering: {} with data: {}".format(template_abs_path, data))

    with open(template_abs_path) as t:
        template = jinja2.Template(t.read())

    tmp_output_html = '{}/rendered.html'.format(TMPFILE_FOLDER)
    with open(tmp_output_html, 'w') as f:
        rendered_html = template.render(**data)
        f.write(rendered_html)

    get_screenshoter(dimensions).take_screenshot(
        "file://"+tmp_output_html, tmp_img_file)


def join_images(img_array, joined_img, dimensions):
    # creates a new empty image, RGB mode, and size 400 by 400.
    def start_image_iter(max_images=10):
        for img_count in range(max_images):
            new_im = Image.new('RGB',
                               size=dimensions.total_size,
                               color=(255, 255, 255, 0))
            dimension_iter = dimensions.iterate_layout()
            joined_img_name = "{}_{}.png".format(joined_img, img_count)
            yield(joined_img_name, new_im, dimension_iter)
        raise ValueError("Too many images")

    image_iter = start_image_iter()
    (joined_img_name, new_im, dimension_iter) = next(image_iter)
    for i, img_file in enumerate(img_array):
        im = Image.open(img_file)
        resized_im = im.resize(dimensions.dimensions, Image.ANTIALIAS)
        try:
            (x, y) = next(dimension_iter)
        except StopIteration:
            print("Output image: {}".format(joined_img_name))
            new_im.save(joined_img_name)
            (joined_img_name, new_im, dimension_iter) = next(image_iter)
            (x, y) = next(dimension_iter)

        new_im.paste(resized_im, (x, y))

    print("Output image: {}".format(joined_img_name))
    new_im.save(joined_img_name)


if __name__ == "__main__":
    cli()
