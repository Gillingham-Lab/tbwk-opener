import numpy as np
from scipy.interpolate import interp1d

from tbwk.RawOpener import Block
from tbwk.Properties import PropertyBag


"""
Block structure
(all is little endian)

The header of each block consists of block type (4 bytes), block size (4 bytes) and 4 empty bytes.

A measurement block (151) contains 3 nested blocks. The blocks content start at 520.
    - 152, Contains a description and the measurement name:
        12 bytes (?)
        1 int8 (length), usually 28
        n char, usually "Thermo Scientific DataCarton"
        8 bytes, usually 00 00 00 00 00 f0 3f. Might be float64 for "1.0"
        1 int8 (length)
        n char, contains the measurement name
        12 bytes, usually 3 int32: [1, 1, 0]
    - 920, a wrapper for another block.
        12 bytes (?)
        Then another subblock starts with FE FF FF FF, with the content starting at offset 520 again.
        - 921
            12 bytes
            1 int8 (length), usually 29
            n char, usually "Thermo Scientific UV Spectrum"
            8 bytes, usually 00 00 00 00 00 f0 3f.
        - 922
            12 bytes
            \n
            4 bytes
        - 930
            12 bytes
            Then another subblock starts with FE FF FF FF, offset at 520
            - 931
                12 bytes
                1 int8 (length), usually 30
                n char, usually "Thermo Scientific Data-Vector " (sic)
                1 int8 (length), usually 29
                n char, usually "SpectrumFileFormat.UVSpectrum"
                1 int8 (length)
                n char, measurement name again.
                8 bytes, windows filetime, eg 97 dc af d7 2c 46 d6 01 = 2020-06-19 13:29:06.5140375 (+2)
            - 932
                y values.
                y label at offset 59, containing axis label in long and short:
                    1 int8
                    n char
                    1 int8
                    n char
                    8 bytes
                    21 bytes
                    1 int32 (4 bytes) indicating number of floats
                    n float64 containing y values
            - 932
                x values
                y label at offset 59, containing axis label in long and short:
                    1 int8
                    n char
                    1 int8 (usually 0)
                    n char (empty)
                    8 bytes
                    21 bytes
                    1 int32 (4 bytes) indicating number of floats
                    n float64 containing y values
        - 990 (10X?)
            - All contain XML data.
        
    - 62, content starts commonly at 520 after the block header.
        12 bytes (?)
        n char, XML content
"""


class Measurement:
    title: str = None

    x_values: np.ndarray = None
    x_label: str = None

    y_values: np.ndarray = None
    y_label: str = None

    properties: PropertyBag = None

    def __init__(self,
                 title: str,
                 x_values: np.ndarray,
                 x_label: str,
                 y_values: np.ndarray,
                 y_label: str,
                 properties: PropertyBag = None,
                 ):
        """

        :param title: Title of the measurement
        :param x_values: numpy array containing x values
        :param x_label: label for x values
        :param y_values: numpy array containing y values (must be equal size)
        :param y_label: label for y values
        :param properties: A property bag
        """
        assert len(x_values) == len(y_values)

        self.title = title

        self.x_values = x_values
        self.x_label = x_label

        self.y_values = y_values
        self.y_label = y_label

        self.properties = properties

    def __repr__(self) -> str:
        return f"<Measurement[{self.title}], {self.properties.get_method_title()}>"

    @classmethod
    def from_block(cls, block):
        assert block.type == Block.Measurement

        # Create a property bag
        properties = PropertyBag.from_xml(block.parsed_content[2].parsed_content)

        # Create new measurement classes
        ret = cls(
            title=block.parsed_content[0].parsed_content[1].decode("utf8"),
            x_values=block.parsed_content[1].parsed_content[2].parsed_content[2].parsed_content[3],
            x_label=block.parsed_content[1].parsed_content[2].parsed_content[2].parsed_content[0].decode("utf8"),
            y_values=block.parsed_content[1].parsed_content[2].parsed_content[1].parsed_content[3],
            y_label=block.parsed_content[1].parsed_content[2].parsed_content[1].parsed_content[0].decode("utf8"),
            properties=properties,
        )

        return ret

    def get_absorption_at(self, wavelength: float, from_spectrum=False) -> float:
        """ Returns the absorption at a given wavelength.

        If from_spectrum is set to true, the value comes always from the spectrum. If set to False, the measured
        values are tried first. """
        value = None

        if from_spectrum is False:
            wavelength_id = f"A{wavelength:.0f}"

            if self.properties.has_property(wavelength_id):
                value = self.properties.get_property(wavelength_id)
                return value.get_value().get_value()

        # Try if we find the measured value exactly
        f = np.isin(self.x_values, wavelength, assume_unique=True)
        result = self.y_values[f]

        if len(result) == 1:
            return result.item()

        # If this does not work, we need to intrapolate
        f = interp1d(self.x_values, self.y_values)

        return f(wavelength)


