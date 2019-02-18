#!/usr/bin/env python
import click
import pageshot

# based on 9*6 requirements for 4096 * 4096
DIMENSION = (682, 455)


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
    url = "file:///Users/borislau/personal/card_maker/example_game/layout.html"
    s = pageshot.Screenshoter(width=DIMENSION[0], height=DIMENSION[1])

    s.take_screenshot(url, output)

    print("Output: {}".format(output))

    # layout png in sequential format


if __name__ == "__main__":
    cli()
