import os

import jinja2
import logging
from typing import Dict
import tempfile
from typing import List

from playtest_cards.img_render import generate_screenshot, join_images
from playtest_cards.dimensions import Dimension
from playtest_cards.utils import SequentialFilename


def render_html(
    data: Dict, root_path, output_html_file=None, template_col="template_file"
) -> str:
    """Render the required template into given htmls
    :return: html string for testing
    """
    template = data[template_col]
    template_abs_path = "{}/{}".format(root_path, template)
    logging.info("Rendering: {} with data: {}".format(template_abs_path, data))

    with open(template_abs_path) as t:
        template = jinja2.Template(t.read())

    if output_html_file:
        with open(output_html_file, "w") as f:
            rendered_html = template.render(**data)
            f.write(rendered_html)

    return rendered_html


def render_all(
    data: List[dict],
    relative_path_for_template,
    output_folder,
    output_filename,
    dimensions: Dimension,
    count_col="count",
    template_col="template_file",
    type_col="type",
    type_filter=None,
    temp_folder=None,
    filename="output",
) -> List[str]:
    """Render images

    :return: List of image names
    """
    # For each piece of data, loop through and render all content
    # join each piece of image
    output_images = []

    html_names = SequentialFilename(filename, ext="html", temp_folder=temp_folder)
    img_names = SequentialFilename(filename, ext="png", temp_folder=temp_folder)

    for d in data:
        card_type = d.get(type_col)
        if type_filter is not None and type_filter != card_type:
            logging.warn(f"Skipping card type: {d}")
            continue

        count = d.get(count_col, 1)

        html_file = next(html_names)
        img_file = next(img_names)
        render_html(d, relative_path_for_template, html_file, template_col=template_col)
        generate_screenshot(html_file, img_file, dimensions=dimensions)
        output_images.extend([img_file] * count)

    final_images_iter = SequentialFilename(
        output_filename, ext="png", temp_folder=output_folder
    )
    final_images = join_images(output_images, final_images_iter, dimensions)
    return final_images
