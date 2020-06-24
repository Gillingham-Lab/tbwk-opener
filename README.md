# tbwk-opener
A python package to open and read tbwk files generated from the NanoDrop 2000 software.

## Features
This library has so far only been tested with Nucleic Acid worksheets.

- Can import tbwk files to read measurements contained within the file
- Successfully reads y- and x-values of a recorded spectrum
- Also reports on tabled data contained in the worksheet (such as A260 for nucleic acids, 
or direct nucleic concentration as chosen by the method)

A protein worksheet (no example provided) showed similar behaviour and should work without any issues.

## Installation

Make sure you've installed numpy and scipy before attempting to install tbwk-opener from pip, then use:

```shell script
pip install tbwk-opener
```

## Usage

Get all measurements from a worksheet and report on concentration using the absorption at 260 nm:

```python
from tbwk import Worksheet

worksheet = Worksheet.import_worksheet("examples/nanodrop-dna-measurements-01.twbk")

factor = (2.05 + 2.30)/2 # μM per absorption unit
for measurement in worksheet:
    print(f"{measurement.title:20}{measurement.get_absorption_at(260)*factor:.2f} μM")
```

```text
wash                0.18 μM
blank               0.02 μM
BSD01               61.47 μM
BSD01               61.11 μM
BSD01 cntl A1       37.87 μM
wash                0.57 μM
BSD01 cntl A2       33.94 μM
wash                0.27 μM
BSD01 cntl A3       44.39 μM
BSD01 cntl A3       0.35 μM
BSD01 cntl A4       40.00 μM
wash                0.05 μM
wash                0.02 μM
```