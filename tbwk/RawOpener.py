try:
    import defusedxml.cElementTree as ET
except ImportError:
    try:
        import defusedxml.ElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

import datetime
import numpy as np


class Block:
    """ Represents a "Block" in a tbwk file."""
    Measurement = 151

    head = None
    type = None
    parts = None
    content = None
    offset = None

    def __init__(self, head, type, size, content, offset):
        self.head = head
        self.type = type
        self.size = size
        self.content = content
        self.offset = offset

        if type == 62:
            self.parse_xml()
        elif type == 63:
            self.parse_xml()
        elif type == 150:
            self.parse_150()
        elif type == 151:
            self.parse_subblock()
        elif type == 152:
            self.parse_152()
        elif type == 920:
            self.parse_subblock()
        elif type == 921:
            self.parse_921()
        elif type == 922:
            self.parsed_content = None
        elif type == 930:
            self.parse_subblock()
        elif type == 931:
            self.parse_931()
        elif type == 932:
            self.parse_uv()
        elif type == 990:
            self.parse_xml()
        elif type == 991:
            self.parse_991()
        elif type < 10000:
            raise Exception(f"No clue what block {type} is.")

    def __repr__(self):
        # alt_types = (int.from_bytes(self.head[:1], "little"), int.from_bytes(self.head[1:2], "little"))
        return f"<TBWK-Block {self.type} ({self.describe()}) at offset {self.offset} with size {self.size}>"

    def describe(self):
        if self.type == 63:
            return "Main XML"
        elif self.type == 991:
            return self.parsed_content[0]
        elif self.type == 151:
            return self.parsed_content[0].parsed_content[1]

    def parse_xml(self):
        xml = ET.fromstring(self.content[12:])

        self.parsed_content = xml

    def parse_subblock(self):
        content = self.content[12:]

        self.parsed_content = unpack(content)

    def parse_uv(self):
        content = self.content[59:]
        offset = 0

        length1, label_long = unpack_string(content)
        length2, label_short = unpack_string(content[offset + length1 + 1:])

        offset += 1 + length1 + 1 + length2
        offset += 8  # 8 empty bytes

        offset += 21  # 4 indicating dimension again, followed by int8, then by 2x float64.
        # First of these floats was 1 for 0 for y-axis and 1 for x-axis
        # Second was in both cases 0. Needs more "figuring out".

        number_of_values = int.from_bytes(content[offset:offset + 4], "little")
        values = content[offset + 4:]

        values = np.frombuffer(values, dtype="<f8")

        self.parsed_content = (label_long, label_short, number_of_values, values)

    def parse_921(self):
        length, title = unpack_string(self.content[12:])

        self.parsed_content = title

    def parse_931(self):
        offset = 12

        length, blocktype = unpack_string(self.content[offset:])
        offset += 1 + length

        length, fileformat = unpack_string(self.content[offset:])
        offset += 1 + length

        length, samplename = unpack_string(self.content[offset:])
        offset += 1 + length

        sampletime = unpack_datetime(self.content[offset:])

        self.parsed_content = (blocktype, fileformat, samplename, sampletime)

    def parse_991(self):
        stringLength = int.from_bytes(self.content[12:13], "little")
        objectType = self.content[13:13 + stringLength]
        xml = ET.fromstring(self.content[13 + stringLength:])

        self.parsed_content = (objectType, xml)

    def parse_150(self):
        content = self.content[12:]
        offset = 0

        length, workbook = unpack_string(content)
        offset += length + 1 + 8

        length, workbook_type = unpack_string(content[offset:])
        offset += length + 1 + 12

        length, source = unpack_string(content[offset:])
        offset += length + 1

        length, measurement_type = unpack_string(content[offset:])
        offset += length + 1

        length, application_name = unpack_string(content[offset:])
        offset += length + 1

        length, application_version = unpack_string(content[offset:])
        offset += length + 1

        self.parsed_content = (workbook, workbook_type, source, measurement_type, application_name, application_version)

    def parse_152(self):
        content = self.content[12:]

        length, blocktype = unpack_string(content)
        length, samplename = unpack_string(content[length + 1 + 8:])

        self.parsed_content = (blocktype, samplename)

def unpack_string(content):
    length = content[0]
    string = content[1:1 + length]

    return length, string


def unpack_datetime(filetime_bin):
    """ Converts windows file time to a datetime object.

    Windows file time is a 64bit integer noted in "100 ns since January 1, 1601 UTC"

    For conversion, we need to adjust the epoch first and then convert to seconds.

    Source:
    https://support.microsoft.com/en-za/help/167296/how-to-convert-a-unix-time-t-to-a-win32-filetime-or-systemtime

    """
    assert len(filetime_bin) == 8

    filetime_int = int.from_bytes(filetime_bin, "little")

    unixtime_in_100ns = filetime_int - 116444736000000000 # Shift the epoch to January 1, 1970 UTC
    unixtime_in_s = unixtime_in_100ns * 0.000_000_1 # 0.000_000_1 s/100 ns

    return datetime.datetime.fromtimestamp(unixtime_in_s)


def unpack(content):
    """ Unpacks a file or subfile and returns the individual blocks."""
    assert content[0:4] == b"\xfe\xff\xff\xff"

    header_size = int.from_bytes(content[32:36], "little")

    # Unpack blocks
    blocks = []
    offset = 40 + header_size

    while True:
        block_head = content[offset:offset + 12]

        block_type = int.from_bytes(content[offset:offset + 4], "little")
        block_size = int.from_bytes(content[offset + 4:offset + 8], "little")
        block_none = int.from_bytes(content[offset + 8:offset + 12], "little")

        block = content[offset + 12:offset + 12 + block_size]

        blocks.append(Block(block_head, block_type, block_size, block, offset))

        offset += 12 + block_size

        if offset == len(content):
            break

    return blocks