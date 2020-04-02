import os


from playtest_cards.render import render_all
from playtest_cards.dimensions import Layout
from playtest_cards.source import read_yaml


curr_folder = os.path.dirname(os.path.abspath(__file__))

INPUT_YAML = os.path.join(curr_folder, "../example_game/content.yaml")


def test_render():
    data = read_yaml(INPUT_YAML)

    jpeg_files = render_all(
        data,
        os.path.join(curr_folder, "../example_game/"),
        os.path.join(curr_folder, "../genfile/"),
        "test",
        count_col="count",
        template_col="template_file",
        type_col="type",
        type_filter="bear",
        dimensions=Layout.tts,
    )
    assert len(jpeg_files) == 2, "Got output filename"


if __name__ == "__main__":
    test_render()
