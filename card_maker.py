#!/usr/bin/env python
import os
from typing import List, Dict

import yaml
import click
import jinja2
import pageshot
from PIL import Image

from playtest_cards.dimensions import LAYOUT, Dimension
from playtest_cards.sheets import SheetReader


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
@click.argument('yaml_file')
@click.option('-o', '--output', type=click.STRING, default='out')
@click.option('-i', '--input_layout', type=click.STRING, default='A4')
@click.option('-l', '--layout', type=click.STRING, default='letter',
              help="Output format {}".format(list(LAYOUT.keys())))
def render(yaml_file, output, input_layout, layout):
    all_output_images = []
    img_count = 0
    input_dimensions = LAYOUT[input_layout]

    # Read the yaml file
    yaml_data = filter(lambda x: x, yaml.load_all(open(yaml_file, 'r')))
    image_files = parse_content_from_array(
        yaml_data, dimensions=input_dimensions)
    output_dimensions = LAYOUT[layout]
    join_images(image_files, output, dimensions=output_dimensions)


@cli.command()
@click.argument('content_sheet')
@click.option('-s', '--sheetname', type=click.STRING, default='Sheet1')
@click.option('-o', '--output', type=click.STRING, default='out')
@click.option('-i', '--input_layout', type=click.STRING, default='A4')
@click.option('-l', '--layout', type=click.STRING, default='letter')
@click.option('-t', '--test', is_flag=True, default=False,
              help="Print item in test mode (only first image)")
def render_from_gsheet(content_sheet,
                       sheetname, output, input_layout, layout, test):
    """Given a folder, render the image generated for boardgame simulator
    """
    # layout png in sequential format
    input_dimensions = LAYOUT[input_layout]
    gsheet_data = iter(SheetReader(content_sheet, sheet_name=sheet_name))
    image_files = parse_content_from_array(
        gsheet_data, dimensions=input_dimensions, test=test)
    output_dimensions = LAYOUT[layout]
    join_images(image_files, output, dimensions=output_dimensions)


def parse_content_from_array(data_list, dimensions, test=False):
    all_output_images = []
    img_count = 0
    d: List[Dict[str, any]]
    for d in data_list:
        print("Getting data: {}".format(d))
        images_created = render_card_from_data(d, img_count, dimensions)
        img_count += len(images_created)
        all_output_images.extend(images_created)

        if test:
            break

    return all_output_images


def render_card_from_data(d, total_img_count, dimensions):
    output_images = []

    template_file = d.get('template_file')
    assert template_file, "No template file found in: {}".format(d)
    try:
        count = int(d['count'])
    except KeyError:
        # no key, assume 1
        count = 1
    except ValueError:
        # It has count, but no value provided
        count = 0

    def get_image_name(img_count):
        return '{tmpfolder}/output_{index}.png'.format(
            index=img_count, tmpfolder=TMPFILE_FOLDER
        )
    if count:
        if not d.get('use_index'):
            temp_out_img = get_image_name(total_img_count)
            render_content(d, template_file,
                           temp_out_img, render_path=os.getcwd(),
                           dimensions=dimensions)
            output_images.extend([temp_out_img] * count)
        else:
            for idx in range(count):
                temp_out_img = get_image_name(total_img_count)
                d.update({'index': idx})
                render_content(d, template_file,
                               temp_out_img, render_path=os.getcwd(),
                               dimensions=dimensions)
                output_images.append(temp_out_img)
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


def join_images(img_array: List[str], joined_img: str, dimensions: Dimension):
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
        if not dimensions.potrait:
            im = im.rotate(90, expand=True)
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
