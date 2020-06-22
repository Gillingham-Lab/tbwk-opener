import numpy as np
from typing import Dict, Optional, Tuple


class PropertyBag:
    """ A container for tabled properties from a measurement. """
    method_title: str
    method_description: str
    method_filename: str

    _properties: Dict[str, "Property"]

    def __init__(self):
        self._properties = {}

    def __repr__(self) -> str:
        return f"<PropertyBag: n={len(self._properties)}>"

    def get_method_title(self) -> str:
        return self.method_title

    @classmethod
    def from_xml(cls, xml_tree) -> "PropertyBag":
        """ Creates a property bag from the corresponding xml tree. """
        properties = cls()

        assert xml_tree.tag == "PARAMOBJ"

        # Get the spectrum results
        spectrum_results = list(list(xml_tree)[0])[0]
        assert spectrum_results.attrib["TYPE"] == "ParamProperties.SpectrumResults"

        # Iterate over all var elements
        for element in spectrum_results:
            # Skip non-var elements
            if element.tag != "VAR":
                continue

            var_name = element.attrib["NAME"]

            if var_name == "m_MethodFilename":
                properties.method_filename = element.text.strip()
            elif var_name == "m_MethodTitle":
                properties.method_title = element.text.strip()
            elif var_name == "m_MethodDescription":
                properties.method_description = element.text.strip()
            elif var_name == "m_QuantGroups":
                # m_QuantGroups contains all tabled measurements
                for p in element:
                    if p.tag != "PARAM":
                        continue

                    property = Property.from_xml(p)

                    if property is not None:
                        properties.add_property(property)

        return properties

    def add_property(self, property: "Property") -> None:
        """ Adds a property.
        :param property: A property
        :return:
        """
        self._properties[property.get_id()] = property

    def has_property(self, id: str) -> bool:
        return True if id in self._properties else False

    def get_property(self, id: str) -> "Property":
        return self._properties[id]


class Property:
    _id: str
    _type: str
    _value: "Value"
    _raw: Optional["Value"]

    def __init__(self,
                 id: str,
                 type: str,
                 value: "Value",
                 raw: Optional["Value"] = None,
                 ):
        """

        :param id: Identifier, also known as the property title
        :param type: Property type, commonly equal to the identifier
        :param value: Property value
        :param raw: Raw property value if found.
        """
        self._id = id
        self._type = type
        self._value = value
        self._raw = raw

    def __repr__(self) -> str:
        return f"<Property[{self._id}]: {self._value}>"

    def get_id(self) -> str:
        return self._id

    def get_type(self) -> str:
        return self._type

    def get_value(self) -> "Value":
        return self._value

    def get_raw_value(self) -> Optional["Value"]:
        return self._raw

    @classmethod
    def from_xml(cls, xml_tree) -> Optional["Property"]:
        property_title = None
        property_type = None
        property_value = None
        property_raw = None

        for var in xml_tree:
            if var.tag != "VAR":
                continue

            if var.attrib["NAME"] == "m_Title":
                property_title = var.text.strip()
            elif var.attrib["NAME"] == "m_ResultType":
                property_type = var.text.strip()
            elif var.attrib["NAME"] == "m_QuantElements":
                # m_QuantElements contains multiple param tags with the actual values
                property_value, property_raw = Value.from_xml(var, property_type)

        if property_value is not None:
            property = cls(property_title, property_type, property_value, property_raw)
        else:
            property = None

        return property


class Value:
    """ Represents a value """
    _title: str
    _digits: int
    _value: float
    _unit: Optional[str]
    _factor: Optional[float]

    def __init__(self,
                 title: str,
                 digits: int,
                 value: float,
                 unit: Optional[str] = None,
                 factor: Optional[int] = None
                 ):
        self._title = title
        self._digits = digits
        self._value = value
        self._unit = unit
        self._factor = factor

    def get_value(self):
        return self._value

    def __repr__(self):
        return f"<Value[{self._title}]: {self._value:.{self._digits}f}>"

    @classmethod
    def from_xml(cls, xml_tree, type) -> Tuple[Optional["Value"], Optional["Value"]]:
        value = None
        raw_value = None
        title = None
        raw_title = None
        num_digits = None
        raw_num_digits = None
        unit = None
        factor = None

        params = {}

        for param in xml_tree:
            if param.tag != "PARAM":
                continue

            element = {}
            for var in param:
                if var.tag != "VAR":
                    continue

                converted_value = var.text.strip()

                if var.attrib["TYPE"] == "System.Double":
                    converted_value = float(converted_value)
                elif var.attrib["TYPE"] == "System.Int32":
                    converted_value = int(converted_value)

                element[var.attrib["NAME"]] = converted_value

            params[element["m_ResultType"]] = element

        if type in params:
            value = params[type]["m_Value"]
            num_digits = params[type]["m_NumDigits"]
            title = params[type]["m_Title"]

            if type + "Unit" in params:
                unit = params[type + "Unit"]["m_Value"]

            if type + "Factor" in params:
                factor = params[type + "Factor"]["m_Value"]

        if type + "Raw" in params:
            raw_value = params[type + "Raw"]["m_Value"]
            raw_num_digits = params[type + "Raw"]["m_NumDigits"]
            raw_title = params[type + "Raw"]["m_Title"] + "Raw"

        if value is not None:
            tabled_value = cls(title, num_digits, value, unit, factor)
        else:
            tabled_value = None

        if raw_title is not None:
            raw_value = cls(raw_title, raw_num_digits, raw_value)
        else:
            raw_value = None

        return tabled_value, raw_value


