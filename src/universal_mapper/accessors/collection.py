from collections.abc import Collection, Iterator, Mapping
from typing import Any

from universal_mapper.accessors.abstract_base import (
    InstanceMappingAccessor,
    TypeMappingAccessor,
)
from universal_mapper.type_utils import TypeExtractor, get_type_from_composite_type


def _can_map[T](target: TypeExtractor[T]) -> bool:
    return (
        issubclass(target.get_origin(), Collection)
        and not issubclass(target.get_origin(), Mapping)
        and not target.is_primitive()
    )


class CollectionTypeAccessor[T: Collection[Any]](TypeMappingAccessor[T, int, Any]):
    def __init__(self, accessor_type: type[T]):
        self.__accessor_type = accessor_type
        self.__target_value_type: type = get_type_from_composite_type(accessor_type)
        self.__container: list[Any] = []

    @classmethod
    def can_map(cls, target: TypeExtractor[T]) -> bool:
        return _can_map(target)

    def get_value_type(self, key: int) -> Any:
        return self.__target_value_type

    def __contains__(self, key: int) -> bool:
        return key <= len(self.__container)

    def __setitem__(self, key: int, value: Any) -> None:
        self.__container.append(value)

    def render(self) -> T:
        return self.__accessor_type(self.__container)  # type: ignore


class CollectionInstanceAccessor[T: Collection[Any]](
    InstanceMappingAccessor[T, int, Any]
):
    def __init__(self, accessor_type: type[T], instance: T):
        self.__accessor_type = accessor_type
        self.__instance: T = instance

    @classmethod
    def can_map(cls, target: TypeExtractor[T]) -> bool:
        return _can_map(target)

    def get_value_type(self, key: int) -> Any:
        return type(self.__instance[key])  # type: ignore [index]

    def __contains__(self, item: int) -> bool:
        return item < len(self.__instance)

    def __getitem__(self, key: int) -> Any:
        return self.__instance[key]  # type: ignore [index]

    def __setitem__(self, key: int, value: Any) -> None:
        self.__instance[key] = value  # type: ignore [index]

    def __iter__(self) -> Iterator[tuple[int, Any]]:
        return enumerate(self.__instance)

    def render(self) -> T:
        return self.__instance
