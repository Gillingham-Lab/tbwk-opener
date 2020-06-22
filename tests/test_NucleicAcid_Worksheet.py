import unittest

from tbwk import Worksheet


class NucleicAcidWorksheetTestCase(unittest.TestCase):
    def setUp(self):
        filenames = [
            "examples/nanodrop-dna-measurements-01.twbk",
            "examples/nanodrop-dna-measurements-02.twbk",
        ]

        worksheets = []

        for file in filenames:
            worksheets.append(Worksheet.import_worksheet(file))

        self.worksheets = worksheets

    def test_number_of_measurements(self):
        number_of_experiments = [
            13, 6,
        ]

        for i in range(len(self.worksheets)):
            should = number_of_experiments[i]
            actual = len(self.worksheets[i])

            self.assertEqual(should, actual)

    def test_measurements_titles(self):
        measurement_titles = [
            ["wash", "blank", "BSD01", "BSD01", "BSD01 cntl A1", "wash", "BSD01 cntl A2",
             "wash", "BSD01 cntl A3", "BSD01 cntl A3", "BSD01 cntl A4", "wash", "wash"],
            ["blank", "blank", "CF2", "CF1", "wash", "wash"],
        ]

        for i in range(len(self.worksheets)):
            worksheet = self.worksheets[i]

            for j in range(len(worksheet)):
                should = measurement_titles[i][j]
                actual = worksheet.measurements[j].title

                self.assertEqual(should, actual)

    def test_measurements_axes(self):
        x_should = "Wavelength (nm)"
        y_should = "10mm Absorbance"

        for i in range(len(self.worksheets)):
            worksheet = self.worksheets[i]

            for j in range(len(worksheet)):
                x_actual = worksheet.measurements[i].x_label
                y_actual = worksheet.measurements[i].y_label

                self.assertEqual(x_should, x_actual, msg="X-Axis label not matching.")
                self.assertEqual(y_should, y_actual, msg="Y-Axis label not matching.")
