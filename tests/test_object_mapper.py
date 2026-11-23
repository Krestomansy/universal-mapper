from decimal import Decimal
from typing import Literal

from universal_mapper import ObjectMapper


class SomeNestedObject:
    def __init__(self, field_a: str, field_b: str | None = None):
        self.field_a = field_a
        self.field_b = field_b

    def __repr__(self) -> str:
        return f"SomeNestedObject(field_a={self.field_a}, field_b={self.field_b})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.field_a == other.field_a and self.field_b == other.field_b


class SomeObject:
    def __init__(self, field_1: str | None, field_2: dict[str, SomeNestedObject]):
        self.field_1 = field_1
        self.field_2 = field_2

    def __repr__(self) -> str:
        return f"SomeObject(field_1={self.field_1}, field_2={self.field_2})"


class SomeOtherObject:
    def __init__(self, field_2: dict[str, SomeNestedObject] | None):
        self.field_2 = field_2

    def __repr__(self) -> str:
        return f"SomeObject(field_2={self.field_2})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.field_2 == other.field_2


class TestObjectMapper:
    def test_none_source_and_custom_mapping(self) -> None:
        """Map a None source directly and with a custom mapping function."""
        mapper = ObjectMapper()
        assert mapper.map(None).to(str) is None

        mapper.add_mapping(str, lambda source: "missing" if source is None else str(source))
        assert mapper.map(None).to(str) == "missing"

    def test_automapping_nested_generic_objects(self) -> None:
        """Map ordinary Python objects containing nested objects."""
        # Arrange
        mapper = ObjectMapper()
        obj_start = SomeObject(
            "some_value",
            {
                "1": SomeNestedObject("nested_value1", "opt_value"),
                "2": SomeNestedObject("nested_value2"),
            },
        )
        obj_expected = SomeOtherObject(
            {
                "1": SomeNestedObject("nested_value1", "opt_value"),
                "2": SomeNestedObject("nested_value2"),
            }
        )
        # Act
        obj_result = mapper.map(obj_start).to(SomeOtherObject)
        assert obj_result == obj_expected

    def test_merging_into_nested_generic_objects(self) -> None:
        """Merge into ordinary Python objects containing nested objects."""
        # Arrange
        mapper = ObjectMapper()
        obj_start = SomeOtherObject(
            field_2={
                "1": SomeNestedObject("nested_value1", "opt_value"),
                "2": SomeNestedObject("nested_value2"),
            }
        )
        obj_new = SomeOtherObject(field_2={"2": SomeNestedObject("nested_value2", "new_value")})
        obj_expected = SomeOtherObject(
            field_2={
                "1": SomeNestedObject("nested_value1", "opt_value"),
                "2": SomeNestedObject("nested_value2", "new_value"),
            }
        )

        # Act
        obj_result = mapper.map(obj_new).to(obj_start)
        assert obj_result == obj_expected

    def test_merging_lists(self) -> None:
        """Update one list with another."""
        # Arrange
        mapper = ObjectMapper()
        initial_list = [1, 2, 3]
        other_list = [10, 20]
        # Act
        mapper.map(other_list).to(initial_list)
        # Assert
        assert initial_list == [10, 20, 3]

    def test_primitive_literal_mapping(self) -> None:
        # Arrange
        mapper = ObjectMapper()
        # Act
        result = mapper.map("edit").to(Literal["edit", "saved"])
        # Assert
        assert str(result) == "edit"

    def test_primitive_float_to_decimal_mapping(self) -> None:
        # Arrange
        mapper = ObjectMapper()
        # Act
        result = mapper.map(1.25).to(Decimal)
        # Assert
        assert result == Decimal("1.25")

    def test_primitive_decimal_to_float_mapping(self) -> None:
        # Arrange
        mapper = ObjectMapper()
        # Act
        result = mapper.map(Decimal("1.25")).to(float)
        # Assert
        assert result == 1.25

    def test_primitive_decimal_to_int_mapping(self) -> None:
        # Arrange
        mapper = ObjectMapper()
        # Act
        result = mapper.map(Decimal(123)).to(int)
        # Assert
        assert result == 123

    def test_list_index_rules(self) -> None:
        """Use custom rules for specific list indices."""
        # Arrange
        mapper = ObjectMapper()
        mapper.add_mapping(
            map_to=list[str],
            mapping={
                1: lambda a: str(a[1]).capitalize(),
                2: lambda a: str(a[2]).upper(),
            },
        )
        initial_list = ["check", "this", "out", ":)"]

        # Act
        result = mapper.map(initial_list).to(list[str])

        # Assert
        assert result == ["check", "This", "OUT", ":)"]
