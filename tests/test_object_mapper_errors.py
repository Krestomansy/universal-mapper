from __future__ import annotations

from decimal import Decimal
from typing import Literal

import pytest

from universal_mapper import ObjectMapper
from universal_mapper.exceptions import CircularReferenceError, TypeMismatchError


class CircularRefA:
    def __init__(self, b: CircularRefB | None = None) -> None:
        self.b = b


class CircularRefB:
    def __init__(self, a: CircularRefA | None = None) -> None:
        self.a = a


class SimpleObject:
    def __init__(self, field_a: str):
        self.field_a = field_a


class TestObjectMapperErrors:
    def test_circular_reference_error(self) -> None:
        """Raise CircularReferenceError when circular references are detected."""
        # Arrange
        mapper = ObjectMapper()
        obj_a = CircularRefA()
        obj_b = CircularRefB(obj_a)
        obj_a.b = obj_b

        # Act & Assert
        with pytest.raises(CircularReferenceError):
            mapper.map(obj_a).to(CircularRefA)

    def test_primitive_type_mismatch(self) -> None:
        # Arrange
        mapper = ObjectMapper()
        string = "hello world"

        # Act & Assert
        with pytest.raises(TypeMismatchError):
            mapper.map(string).to(int)

    def test_primitive_literal_mapping_mismatch(self) -> None:
        # Arrange
        mapper = ObjectMapper()

        # Act & Assert
        with pytest.raises(TypeMismatchError):
            mapper.map("archived").to(Literal["edit", "saved"])

    def test_not_implemented_error_for_factories(self) -> None:
        # Arrange
        mapper = ObjectMapper()

        # Act & Assert
        with pytest.raises(NotImplementedError):
            mapper.map(object()).to(SimpleObject)

        with pytest.raises(NotImplementedError):
            mapper.map(SimpleObject("value")).to(object)

    def test_decimal_conversion_error(self) -> None:
        """Should raise TypeMismatchError when converting an invalid string to Decimal."""
        # Arrange
        mapper = ObjectMapper()
        invalid_string = "not a decimal"

        # Act & Assert
        with pytest.raises(TypeMismatchError):
            mapper.map(invalid_string).to(Decimal)

    def test_decimal_to_int_with_fraction_error(self) -> None:
        """Should raise TypeMismatchError when converting a Decimal with a fraction to int."""
        # Arrange
        mapper = ObjectMapper()
        decimal_with_fraction = Decimal("123.45")

        # Act & Assert
        with pytest.raises(TypeMismatchError):
            mapper.map(decimal_with_fraction).to(int)
