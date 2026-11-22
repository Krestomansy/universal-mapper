from abc import abstractmethod
from collections.abc import Iterator
from typing import Any

from universal_mapper.accessors.abstract_base import (
    InstanceMappingAccessor,
    TypeMappingAccessor,
)
from universal_mapper.type_utils import TypeExtractor


class ObjectAccessorMixin[T: object]:
    @classmethod
    @abstractmethod
    def _can_map(cls, target: TypeExtractor[T]) -> bool: ...

    @abstractmethod
    def get_fields(self, target_cls: type[T]) -> list[str]: ...

    @abstractmethod
    def get_field_type(self, target_cls: type[T], field: str) -> Any: ...

    @abstractmethod
    def skip_instance_field(self, instance: T, field: str) -> bool: ...

    @abstractmethod
    def create_instance(self, target_cls: type[T], data_dict: dict[str, Any]) -> T: ...


class ObjectTypeAccessor[T: object](
    TypeMappingAccessor[T, str, Any], ObjectAccessorMixin[T]
):
    def __init__(self, accessor_type: type[T]):
        self.__accessor_type = accessor_type
        self.__fields = self.get_fields(accessor_type)
        self.__container: dict[Any, Any] = {}

    @classmethod
    def can_map(cls, target: TypeExtractor[T]) -> bool:
        return cls._can_map(target)

    def get_value_type(self, key: str) -> Any:
        return self.get_field_type(self.__accessor_type, key)

    def __contains__(self, item: Any) -> bool:
        return item in self.__fields

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__container[key] = value

    def render(self) -> T:
        return self.create_instance(self.__accessor_type, self.__container)


class ObjectInstanceAccessor[T: object](
    InstanceMappingAccessor[T, str, Any], ObjectAccessorMixin[T]
):
    def __init__(self, accessor_type: type[T], instance: T):
        self.__accessor_type = accessor_type
        self.__fields = self.get_fields(accessor_type)
        self.__instance = instance

    @classmethod
    def can_map(cls, target: TypeExtractor[T]) -> bool:
        return cls._can_map(target)

    def get_value_type(self, key: str) -> Any:
        return self.get_field_type(self.__accessor_type, key)

    def __contains__(self, item: Any) -> bool:
        return item in self.__fields and not self.skip_instance_field(
            self.__instance, item
        )

    def __getitem__(self, key: Any) -> Any:
        return getattr(self.__instance, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        setattr(self.__instance, key, value)

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for field in self.__fields:
            if not self.skip_instance_field(self.__instance, field):
                yield (field, getattr(self.__instance, field))

    def render(self) -> T:
        return self.__instance
