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
