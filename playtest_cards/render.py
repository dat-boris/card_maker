import os
import re
import shutil
import logging
from typing import Dict, List, Optional
import tempfile

import jinja2

from playtest_cards.img_render import generate_screenshot, join_images
from playtest_cards.dimensions import Dimension
from playtest_cards.utils import SequentialFilename


def render_html(
    data: Dict, root_path, output_html_file=None, template_col=None,
    dimensions: Optional[Dimension]=None
) -> str:
    """Render the required template into given htmls
    :return: html string for testing
    """
    if template_col is None:
        template_col = "template_file"
    template = data[template_col]
    if not template:
        raise RuntimeError(
            "Not rendering without template file name: {}".format(data))
    template_abs_path = "{}/{}".format(root_path, template)
    logging.info("Rendering: {} with data: {}".format(template_abs_path, data))

    with open(template_abs_path) as t:
        template = jinja2.Template(t.read())

    if output_html_file:
        with open(output_html_file, "w") as f:
            if dimensions:
                data['render_width'] = dimensions.dimensions[0]
                data['render_height'] = height = dimensions.dimensions[1]
            rendered_html = template.render(**data)
            f.write(rendered_html)

    return rendered_html


def __copy_file(src: str, dst: str, extensions: List[str]):
    # ignore any files but files with '.h' extension
    for item in os.listdir(src):
        if any([item.endswith(e) for e in extensions]):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            shutil.copy2(s, d)


def __normalize_col_name(d):
    return {
        re.sub(r'[^\w]', '_', k.lower()): v
        for k, v in d.items()
    }


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
    # We need to copy assets into the render folder
    include_extensions=[".png"],
    normalize_col_name=False,
) -> List[str]:
    """Render images

    :return: List of image names
    """
    # For each piece of data, loop through and render all content
    # join each piece of image
    output_images = []

    if temp_folder is None:
        temp_folder = tempfile.gettempdir()

    html_names = SequentialFilename(
        filename, ext="html", temp_folder=temp_folder)
    img_names = SequentialFilename(
        filename, ext="png", temp_folder=temp_folder)

    for d in data:
        if normalize_col_name:
            d = __normalize_col_name(d)
        card_type = d.get(type_col)
        if type_filter is not None and type_filter != card_type:
            logging.warn(f"Skipping card type: {d}")
            continue

        count = int(d.get(count_col, 1) or 1)

        html_file = next(html_names)
        img_file = next(img_names)
        try:
            output_html = render_html(d, relative_path_for_template, html_file,
                                      template_col=template_col,
                                      dimensions=dimensions
                                      )
        except RuntimeError as e:
            logging.warning(e)
            continue
        __copy_file(relative_path_for_template,
                    temp_folder, include_extensions)

        generate_screenshot(html_file, img_file, dimensions=dimensions)
        output_images.extend([img_file] * count)

    final_images_iter = SequentialFilename(
        output_filename, ext="jpg", temp_folder=output_folder
    )
    final_images = join_images(output_images, final_images_iter, dimensions)
    return final_images
