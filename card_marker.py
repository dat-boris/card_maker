#!/usr/bin/env python
import os

import yaml
import click
import jinja2
import pageshot
from PIL import Image


class Dimension:
    """Record dimension of the print layout"""

    def __init__(self, dimensions, image_layout):
        self.dimensions = dimensions
        self.image_layout = image_layout

    @property
    def total_images(self):
        return self.image_layout[0] * self.image_layout[1]

    @property
    def total_size(self):
        return (
            self.dimensions[0]*self.image_layout[0],
            self.dimensions[1]*self.image_layout[1]
        )

    def __len__(self):
        return self.image_layout[0] * self.image_layout[1]

    def iterate_layout(self):
        """ Return a set of x, y layout on the sheet
        """
        for i in range(len(self)):
            x = (i % self.image_layout[0]) * self.dimensions[0]
            y = i // self.image_layout[0] * self.dimensions[1]
            yield (x, y)


# Define layout of different print types
LAYOUT = {
    # based on 9*6 requirements for 4096 * 4096
    'boardgame': Dimension((455, 682), (9, 6)),
    # 2480 pixels x 3508 pixels (print resolution)
    'paper': Dimension((2480 // 4, 3508//4), (4, 4))
}

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
@click.argument('content_yaml')
@click.option('-o', '--output', type=click.STRING, default='out')
@click.option('-l', '--layout', type=click.STRING, default='paper')
def render(content_yaml, output, layout):
    """Given a folder, render the image generated for boardgame simulator
    """
    # layout png in sequential format
    dimensions = LAYOUT[layout]
    image_files = parse_content(content_yaml, dimensions=dimensions)
    join_images(image_files, output, dimensions=dimensions)


def parse_content(content_file, dimensions):
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
                           temp_out_img, render_path=content_path,
                           dimensions=dimensions)
            count = d.get('count', 1)
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
