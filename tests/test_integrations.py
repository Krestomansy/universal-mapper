from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel, Field

pytest.importorskip("sqlalchemy")
from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, deferred, mapped_column, relationship

from universal_mapper import ObjectMapper


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


class ModifiedUserDto(BaseModel):
    id: str
    name: str


class Base(DeclarativeBase):
    pass


class UserDataOrm(Base):
    __tablename__ = "user_data"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    tag: Mapped[str] = mapped_column(String(255))
    amount: Mapped[int] = mapped_column(default=0)
    description: Mapped[str | None]

    user: Mapped[UserOrm] = relationship(
        "UserOrm",
        back_populates="userdata",
    )

    def __repr__(self) -> str:
        return (
            f"UserDataOrm(id={self.id}, "
            f"user_id={self.user_id}, "
            f"tag={self.tag}, "
            f"amount={self.amount}, "
            f"description={self.description})"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
            and self.user_id == other.user_id
            and self.amount == other.amount
            and self.description == other.description
        )


class UserOrm(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    userdata: Mapped[list[UserDataOrm]] = relationship(
        "UserDataOrm",
        back_populates="user",
    )

    some_property: Mapped[int] = deferred(
        select(func.count(UserDataOrm.id)).where(UserDataOrm.user_id == id).scalar_subquery()
    )

    def __repr__(self) -> str:
        return (
            f"UserOrm(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, userdata={self.userdata})"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
            and self.first_name == other.first_name
            and self.last_name == other.last_name
            and self.userdata == other.userdata
        )


class TestObjectMapper:
    def test_automapping_one_object(self) -> None:
        """Map an object."""
        # Arrange
        mapper = ObjectMapper()
        user_data_start = UserDataDto(id="id", user_id="user_id", tag="test")
        # Act
        user_data_orm = mapper.map(user_data_start).to(UserDataOrm)
        user_data_result = mapper.map(user_data_orm).to(UserDataDto)
        # Assert
        assert user_data_start == user_data_result

    def test_automapping_list_of_objects(self) -> None:
        """Map a list of objects."""
        mapper = ObjectMapper()
        user_data_1 = UserDataDto(id="id1", user_id="user_id", tag="test1")
        user_data_2 = UserDataDto(id="id2", user_id="user_id", tag="test2")
        user_data_3 = UserDataDto(id="id3", user_id="user_id", tag="test3")
        initial_list = [user_data_1, user_data_2, user_data_3]
        user_data_orm_list = mapper.map(initial_list).to(list[UserDataOrm])
        result_list = mapper.map(user_data_orm_list).to(list[UserDataDto])
        assert initial_list == result_list

    def test_automapping_dict_of_objects(self) -> None:
        """Map a dictionary of objects."""
        mapper = ObjectMapper()
        user_data_1 = UserDataDto(id="id1", user_id="user_id", tag="test1")
        user_data_2 = UserDataDto(id="id2", user_id="user_id", tag="test2")
        user_data_3 = UserDataDto(id="id3", user_id="user_id", tag="test3")
        initial_dict = {1: user_data_1, 2: user_data_2, 3: user_data_3}
        user_data_orm_dict = mapper.map(initial_dict).to(dict[int, UserDataOrm])
        result_dict = mapper.map(user_data_orm_dict).to(dict[int, UserDataDto])
        assert initial_dict == result_dict

    def test_automapping_dict_of_lists_of_objects(self) -> None:
        """Map a dictionary of objects."""
        mapper = ObjectMapper()
        user_data_1 = UserDataDto(id="id1", user_id="user_id", tag="test1")
        user_data_2 = UserDataDto(id="id2", user_id="user_id", tag="test2")
        user_data_3 = UserDataDto(id="id3", user_id="user_id", tag="test3")
        initial_dict = {
            "entry_one": [user_data_1, user_data_2],
            "entry_two": [user_data_3],
        }
        user_data_orm_dict = mapper.map(initial_dict).to(dict[str, list[UserDataOrm]])
        result_dict = mapper.map(user_data_orm_dict).to(dict[str, list[UserDataDto]])
        assert initial_dict == result_dict

    def test_automapping_nested_objects(self) -> None:
        """Map an object containing nested objects."""
        # Arrange
        mapper = ObjectMapper()
        user_start = UserDto(
            id="user_id",
            first_name="Ivan",
            last_name="Ivanov",
            userdata=[
                UserDataDto(id="id1", user_id="user_id", tag="test"),
                UserDataDto(id="id2", user_id="user_id", tag="test"),
                UserDataDto(id="id3", user_id="user_id", tag="test"),
            ],
        )
        # Act
        user_orm = mapper.map(user_start).to(UserOrm)
        user_result = mapper.map(user_orm).to(UserDto)
        # Assert
        assert user_start == user_result

    def test_lambda_mapping(self) -> None:
        """Use lambda expressions for mapping."""
        # Arrange
        mapper = ObjectMapper()
        mapper.add_mapping(
            ModifiedUserDto,
            {"name": lambda a: f"{str(a.first_name).upper()} {str(a.last_name).upper()}"},
        )
        user_orm = UserOrm(id="id", first_name="Ivan", last_name="Ivanov")
        # Act
        user_result = mapper.map(user_orm).to(ModifiedUserDto)
        # Assert
        assert user_result == ModifiedUserDto(id="id", name="IVAN IVANOV")

    def test_function_mapping(self) -> None:
        """Use a function for mapping."""
        # Arrange
        mapper = ObjectMapper()

        def mapping_func(_: UserOrm) -> UserDto:
            return UserDto(id="func_id", first_name="func_name1", last_name="func_name2")

        mapper.add_mapping(UserDto, mapping_func)
        user_orm = UserOrm(id="id", first_name="name1", last_name="name2")
        # Act
        user_dto = mapper.map(user_orm).to(UserDto)
        # Arrange
        assert user_dto == UserDto(id="func_id", first_name="func_name1", last_name="func_name2")

    def test_merging_different_classes(self) -> None:
        """Merge into an object of a different class."""
        # Arrange
        mapper = ObjectMapper()
        existing_orm = UserOrm(id="id", first_name="name1", last_name="name2")
        update_data_data = UserUpdateDto(first_name="new_name")
        # Act
        mapper.map(update_data_data).to(existing_orm)
        # Assert
        assert existing_orm == UserOrm(id="id", first_name="new_name", last_name="name2")

    def test_merging_into_nested_objects(self) -> None:
        """Merge into an object with nested fields."""
        # Arrange
        mapper = ObjectMapper()
        user_initial_orm = UserOrm(
            id="user_id",
            first_name="Ivan",
            last_name="Ivanov",
            userdata=[
                UserDataOrm(id="id1", user_id="user_id", tag="test"),
                UserDataOrm(id="id2", user_id="user_id", tag="test"),
                UserDataOrm(id="id3", user_id="user_id", tag="test"),
            ],
        )
        user_update_data = UserUpdateDto(
            first_name="New name",
            userdata=[
                UserDataUpdateDto(tag="new_tag"),
                UserDataUpdateDto(tag="new_tag"),
                UserDataUpdateDto(tag="new_tag"),
            ],
        )
        user_expected_orm = UserOrm(
            id="user_id",
            first_name="New name",
            last_name="Ivanov",
            userdata=[
                UserDataOrm(id="id1", user_id="user_id", tag="new_tag"),
                UserDataOrm(id="id2", user_id="user_id", tag="new_tag"),
                UserDataOrm(id="id3", user_id="user_id", tag="new_tag"),
            ],
        )
        # Act
        mapper.map(user_update_data).to(user_initial_orm)
        # Assert
        assert user_initial_orm == user_expected_orm
