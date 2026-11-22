import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel

from universal_mapper import ObjectMapper
from universal_mapper.exceptions import UnknownTargetTypeError


class UnionErrorDto(BaseModel):
    field: str | int


class HeterogenousTupleErrorDto(BaseModel):
    field: tuple[int, str]


class ListWithoutArgsDto(BaseModel):
    field: list  # type: ignore[type-arg]


class DictWithoutArgsDto(BaseModel):
    field: dict  # type: ignore[type-arg]


class ListWithUnionDto(BaseModel):
    field: list[int | str]


class DictWithUnionKeyDto(BaseModel):
    field: dict[str, str | float]


class TestObjectMapperErrors:
    def test_unknown_target_type_for_union(self) -> None:
        """Raise UnknownTargetTypeError for a union with multiple types."""
        # Arrange
        mapper = ObjectMapper()
        obj = UnionErrorDto(field="some_value")

        # Act & Assert
        with pytest.raises(UnknownTargetTypeError):
            mapper.map(obj).to(UnionErrorDto)

    def test_not_implemented_for_heterogenous_tuple(self) -> None:
        """Raise an error for a tuple with multiple types."""
        # Arrange
        mapper = ObjectMapper()
        obj = HeterogenousTupleErrorDto(field=(1, "some_value"))

        # Act & Assert
        with pytest.raises(NotImplementedError):
            mapper.map(obj).to(HeterogenousTupleErrorDto)

    def test_unknown_target_type_for_list_without_args(self) -> None:
        """Raise UnknownTargetTypeError for a list without a type argument."""
        # Arrange
        mapper = ObjectMapper()
        obj = ListWithoutArgsDto(field=[1, "a"])

        # Act & Assert
        with pytest.raises(UnknownTargetTypeError):
            mapper.map(obj).to(ListWithoutArgsDto)

    def test_unknown_target_type_for_dict_without_args(self) -> None:
        """Raise UnknownTargetTypeError for a dict without type arguments."""
        # Arrange
        mapper = ObjectMapper()
        obj = DictWithoutArgsDto(field={"key": "value", 2: 2.1})

        # Act & Assert
        with pytest.raises(UnknownTargetTypeError):
            mapper.map(obj).to(DictWithoutArgsDto)

    def test_unknown_target_type_for_list_with_union_arg(self) -> None:
        """Raise UnknownTargetTypeError for a list with a union type argument."""
        # Arrange
        mapper = ObjectMapper()
        obj = ListWithUnionDto(field=[1, "a"])

        # Act & Assert
        with pytest.raises(UnknownTargetTypeError):
            mapper.map(obj).to(ListWithUnionDto)

    def test_unknown_target_type_for_dict_with_union_value(self) -> None:
        """Raise UnknownTargetTypeError for a dict with a union value type."""
        # Arrange
        mapper = ObjectMapper()
        obj = DictWithUnionKeyDto(field={"key": 2.1})

        # Act & Assert
        with pytest.raises(UnknownTargetTypeError):
            mapper.map(obj).to(DictWithUnionKeyDto)
