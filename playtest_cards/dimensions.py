from typing import Tuple


# Always use default width and height
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 1040


class Dimension:
    """Record dimension of the print layout"""

    dimension: Tuple[int, int]
    image_layout: Tuple[int, int]
    protrait: bool

    def __init__(self, dimensions, image_layout, protrait=True):
        self.dimensions = dimensions
        self.image_layout = image_layout
        self.protrait = protrait

    @property
    def total_images(self):
        return self.image_layout[0] * self.image_layout[1]

    @property
    def total_size(self):
        return (
            self.dimensions[0] * self.image_layout[0],
            self.dimensions[1] * self.image_layout[1],
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
class Layout:
    # for tabletop simulator
    # based on 9*6 requirements for 4096 * 4096
    tts = Dimension((4096 // 6, 4096 // 4), (6, 4))
    # vertical
    tts_vertical = Dimension((682, 455), (6, 9))
    # 2480 pixels x 3508 pixels (print resolution)
    A4 = Dimension((2480 // 4, 3508 // 4), (4, 4))
    letter = Dimension((2480 // 4, 3508 // 6), (4, 6))
    # 1240, 877
    letter_landscape = Dimension(
        (3508 // 4, 2480 // 4), (4, 4), protrait=True)
    # Small print out (310x438 per tile)
    letter_tiles = Dimension((2480 // 8, 3508 // 6), (8, 6))
    # See
    tabletopia_card = Dimension(
        (DEFAULT_WIDTH, DEFAULT_HEIGHT), (1, 1), protrait=True)
