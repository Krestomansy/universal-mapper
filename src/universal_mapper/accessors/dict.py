from collections.abc import Iterator, Mapping
from typing import Any

from universal_mapper.accessors.abstract_base import (
    InstanceMappingAccessor,
    TypeMappingAccessor,
)
from universal_mapper.type_utils import TypeExtractor, get_type_from_composite_type


def _can_map(target: TypeExtractor[Mapping[Any, Any]]) -> bool:
    return issubclass(target.get_origin(), Mapping)


class DictTypeAccessor[T: Mapping[Any, Any]](
    TypeMappingAccessor[Mapping[Any, Any], str, Any]
):
    def __init__(self, accessor_type: type[T]):
        self.__accessor_type = accessor_type
        self.__target_value_type: type = get_type_from_composite_type(accessor_type)
        self.__container: dict[Any, Any] = {}

    @classmethod
    def can_map(cls, target: TypeExtractor[Mapping[Any, Any]]) -> bool:
        return _can_map(target)

    def get_value_type(self, key: str) -> Any:
        return self.__target_value_type

    def __contains__(self, item: Any) -> bool:
        return True

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__container[key] = value

    def render(self) -> T:
        return self.__accessor_type(self.__container)  # type: ignore


class DictInstanceAccessor[T: Mapping[Any, Any]](
    InstanceMappingAccessor[Mapping[Any, Any], str, Any]
):
    def __init__(self, accessor_type: type[T], instance: T):
        self.__accessor_type = accessor_type
        self.__instance = instance

    @classmethod
    def can_map(cls, target: TypeExtractor[Mapping[Any, Any]]) -> bool:
        return _can_map(target)

    def get_value_type(self, key: str) -> Any:
        return type(self.__instance[key])

    def __contains__(self, item: Any) -> bool:
        return item in self.__instance

    def __getitem__(self, key: Any) -> Any:
        return self.__instance[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__instance[key] = value  # type: ignore

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        return iter(self.__instance.items())

    def render(self) -> T:
        return self.__instance
