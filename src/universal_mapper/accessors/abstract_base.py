from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from universal_mapper.type_utils import TypeExtractor


class MappingAccessor[T, K, V](ABC):
    @classmethod
    @abstractmethod
    def can_map(cls, target: TypeExtractor[T]) -> bool: ...

    @abstractmethod
    def get_value_type(self, key: K) -> type[V]: ...

    @abstractmethod
    def __contains__(self, key: K) -> bool: ...

    @abstractmethod
    def __getitem__(self, key: K) -> Any | None: ...

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None: ...

    @abstractmethod
    def render(self) -> T: ...


class TypeMappingAccessor[T, K, V](MappingAccessor[T, K, V]):
    @abstractmethod
    def __init__(self, accessor_type: type[T]): ...

    def __getitem__(self, key: K) -> Any | None:
        return None


class InstanceMappingAccessor[T, K, V](MappingAccessor[T, K, V]):
    @abstractmethod
    def __init__(self, accessor_type: type[T], instance: T): ...

    @abstractmethod
    def __iter__(self) -> Iterator[tuple[K, V]]: ...
