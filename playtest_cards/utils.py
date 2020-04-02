import os
import tempfile


class SequentialFilename:
    i: int
    temp_folder: str
    filename: str
    ext: str

    def __init__(self, filename, ext, temp_folder=None):
        if temp_folder is None:
            temp_folder = tempfile.gettempdir()
        self.temp_folder = temp_folder
        self.filename = filename
        self.ext = ext
        self.i = 0

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        filename = os.path.join(
            self.temp_folder, f"{self.filename}_{self.i}.{self.ext}"
        )
        self.i += 1
        return filename
