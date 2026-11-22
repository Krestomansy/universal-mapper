import collections.abc
from collections.abc import Iterator
from typing import Annotated, Any

import pytest

pytest.importorskip("pydantic")
from pydantic import AfterValidator, BaseModel, Field

from universal_mapper import ObjectMapper


class MyCustomCollection[T]:
    def __init__(self, items: collections.abc.Iterable[T]) -> None:
        self._items = list(items)

    def __contains__(self, item: Any) -> bool:
        return item in self._items

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, collections.abc.Collection):
            return list(self._items) == list(other)
        return NotImplemented

    def __repr__(self) -> str:
        return f"MyCustomCollection({self._items})"


class HomogenousTupleDto(BaseModel):
    field: tuple[str, ...]


class UserDataDto(BaseModel):
    id: str
    user_id: str
    tag: str
    amount: int = Field(default=0, ge=0)
    description: str | None = None


class UserDto(BaseModel):
    id: str
    first_name: str
    last_name: str
    userdata: list[UserDataDto] = Field(default_factory=list)


class UserDataUpdateDto(BaseModel):
    user_id: str | None = None
    tag: str | None = None
    amount: int | None = Field(default=None, ge=0)
    description: str | None = None


class UserUpdateDto(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    userdata: list[UserDataUpdateDto] | None = None


def strip_string(v: str) -> str:
    return v.strip()


StrippedString = Annotated[str, AfterValidator(strip_string)]


class AnnotatedPoco(BaseModel):
    name: StrippedString | None


class SimpleSource:
    def __init__(self, name: str):
        self.name = name


class TestObjectMapper:
    def test_automapping_custom_collection(self) -> None:
        """Map a custom collection."""
        # Arrange
        mapper = ObjectMapper()
        user_data_1 = UserDataDto(id="id1", user_id="user_id", tag="test1")
        user_data_2 = UserDataDto(id="id2", user_id="user_id", tag="test2")
        custom_collection = MyCustomCollection([user_data_1, user_data_2])

        expected_list = [user_data_1, user_data_2]

        # Act
        result_list = mapper.map(custom_collection).to(list[UserDataDto])

        # Assert
        assert isinstance(result_list, list)
        assert result_list == expected_list

    def test_homogenous_tuples_allowed(self) -> None:
        """Support tuple[T, ...]."""
        mapper = ObjectMapper()
        initial_obj = HomogenousTupleDto(field=("value1", "value2"))
        assert mapper.map(initial_obj).to(HomogenousTupleDto) == initial_obj

    def test_merging_same_classes(self) -> None:
        """Merge into an object of the same class."""
        # Arrange
        mapper = ObjectMapper()
        existing_dto = UserDto(id="id", first_name="name1", last_name="name2")
        update_data_data = UserUpdateDto(first_name="new_name")
        # Act
        mapper.map(update_data_data).to(existing_dto)
        # Assert
        assert existing_dto == UserDto(id="id", first_name="new_name", last_name="name2")

    def test_custom_rule_for_skipping_fields(self) -> None:
        """Skip fields by specifying None in the field mapping rules."""
        # Arrange
        mapper = ObjectMapper()
        mapper.add_mapping(map_to=UserDto, mapping={"last_name": None})
        existing_dto = UserDto(id="id", first_name="name1", last_name="name2")
        update_data_data = UserUpdateDto(first_name="new_name1", last_name="new_name2")
        # Act
        mapper.map(update_data_data).to(existing_dto)
        # Assert
        assert existing_dto == UserDto(id="id", first_name="new_name1", last_name="name2")

    def test_primitive_rules(self) -> None:
        """Use custom rules for primitive values."""
        # Arrange
        mapper = ObjectMapper()
        mapper.add_mapping(map_to=str, mapping=lambda a: str(a).upper())
        test_dto = UserDto(id="id", first_name="jane", last_name="doe")

        # Act
        mapper.map(test_dto).to(test_dto)

        # Assert
        assert test_dto == UserDto(id="ID", first_name="JANE", last_name="DOE")

    def test_annotated_field_mapping_on_poco(self) -> None:
        """Can map to a class with Annotated fields"""
        # Arrange
        mapper = ObjectMapper()
        source = SimpleSource(name="  test name  ")
        # Act
        target = mapper.map(source).to(AnnotatedPoco)
        # Assert
        assert target.name == "test name"
