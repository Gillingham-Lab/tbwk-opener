import unittest

from tbwk.Properties import Value

class PropertiesValueTestCase(unittest.TestCase):
    test_parameters = [
        {"title": "A title", "digits": 3, "value": 1.26391, "unit": "mg/mL", "factor": 33.0,}
    ]

    def test_getters(self):
        for i in range(len(self.test_parameters)):
            parameters = self.test_parameters[i]

            with self.subTest(i=i, parameters=parameters):
                value = Value(**parameters)

                self.assertEqual(parameters["title"], value.get_title())
                self.assertEqual(parameters["digits"], value.get_digits())
                self.assertAlmostEqual(parameters["value"], value.get_value(), value.get_digits())
                self.assertEqual(parameters["unit"], value.get_unit())
                self.assertAlmostEqual(parameters["factor"], value.get_factor(), 3)

    def test_if_value_gets_formatted_as_expected(self):
        expected = [
            "1.264 mg/mL",
        ]

        for i in range(len(self.test_parameters)):
            parameters = self.test_parameters[i]
            should = expected[i]

            with self.subTest(i=i, parameters=parameters):
                value = Value(**parameters)
                actual = value.get_formatted_value()

                self.assertEqual(should, actual)