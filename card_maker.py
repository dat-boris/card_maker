#!/usr/bin/env python
import os
from typing import List, Dict

import yaml
import click
from playtest_cards.sheets import SheetReader
from playtest_cards.source import read_yaml
from playtest_cards.dimensions import Layout


TMPFILE_FOLDER = os.path.abspath('genfile')
# TODO: using dict from previous usage, can use Layout directly below
LAYOUT = Layout.__dict__

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
    # TODO: use read_yaml properly instead!
    # data_array = read_yaml(yaml_file)
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
    gsheet_data = iter(SheetReader(content_sheet, sheet_name=sheetname))
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




if __name__ == "__main__":
    cli()
