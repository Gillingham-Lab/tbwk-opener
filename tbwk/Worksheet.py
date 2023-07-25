import io
from typing import List, Union
from tbwk.RawOpener import unpack, Block
from tbwk.Measurement import Measurement
import os


class Worksheet:
    measurements: List[Measurement] = None

    def __init__(self):
        self.measurements = []

    def __len__(self) -> int:
        """ Returns the number of measurements within the worksheet. """
        return len(self.measurements)

    def __iter__(self):
        for measurement in self.measurements:
            yield measurement

    def add_measurement(self, measurement: Measurement) -> None:
        """
        Adds a measurement to the worksheet

        :param measurement:
        :return:
        """
        self.measurements.append(measurement)


def import_worksheet(filename: Union[str, io.BytesIO]) -> Worksheet:
    """
    imports a given filename and creates a tbwk.Worksheet object.

    :param filename:
    :return:
    """

    if type(filename) == str and os.path.exists(filename):
        with open(filename, "rb") as fh:
            content = fh.read()
    elif type(filename) == io.BytesIO:
        content = filename.read()
    else:
        content = filename

    if content is None:
        raise FileNotFoundError(f"File {filename} was not found.")

    # Unpack the file
    blocks = unpack(content)

    # Start loading the worksheet with found data.
    worksheet = Worksheet()

    # Add measurements
    for block in blocks:
        if block.type == Block.Measurement:
            # Add a measurement block
            measurement = Measurement.from_block(block)

            worksheet.add_measurement(measurement)
        # ToDo: Import data from other blocks, too.

    return worksheet

