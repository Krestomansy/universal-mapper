from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import (
    Annotated,
    Any,
    Literal,
    TypeVar,
    cast,
    get_args,
    get_origin,
    overload,
)
from uuid import UUID

from universal_mapper.accessors import (
    InstanceMappingAccessor,
    MappingAccessor,
    MappingAccessorFactory,
)
from universal_mapper.exceptions import CircularReferenceError, TypeMismatchError
from universal_mapper.type_utils import TypeExtractor, get_type_from_union_type

type MappingType = Callable[[Any], Any] | dict[str | int, Callable[[Any], Any] | None]
T = TypeVar("T")


class _NullableMapperWrapper:
    """Handle the second part of the mapping process, `.to()`."""

    def __init__(self, from_instance: Any, mapper: ObjectMapper) -> None:
        self._from_instance = from_instance
        self._mapper = mapper

    @overload
    def to(self, to_class_or_instance: type[T]) -> T | None:
        """Map an object to the specified class."""

    @overload
    def to(self, to_class_or_instance: T) -> T | None:
        """Update the fields of the specified object."""

    def to(self, to_class_or_instance: type[T] | T) -> T | None:
        """Map to the specified class or update the fields of the specified object."""
        _visited_ids_stack: set[int] = set()
        return self._mapper._map_internal(
            TypeExtractor(self._from_instance),
            TypeExtractor(to_class_or_instance),
            _visited_ids_stack,
        )


class _MapperWrapper(_NullableMapperWrapper):
    @overload
    def to(self, to_class_or_instance: type[T]) -> T: ...

    @overload
    def to(self, to_class_or_instance: T) -> T: ...

    def to(self, to_class_or_instance: type[T] | T) -> T:
        return cast(T, super().to(to_class_or_instance))


class ObjectMapper:
    """
    Map objects to a specified class, including Pydantic and SQLAlchemy models.

    Mapping can be automatic or configured with rules. Rules can be dictionaries
    of lambda functions for individual fields or complete mapping functions.
    Mapping can create a new object or update an existing object.
    """

    __accessor_factory = MappingAccessorFactory()

    def __init__(self) -> None:
        self._mappings: dict[type[Any], MappingType] = {}

    @classmethod
    def __get_mapping_accessor(
        cls, target: TypeExtractor[T]
    ) -> MappingAccessor[T, Any, Any]:
        return cls.__accessor_factory.get(target)

    def add_mapping(
        self, map_to: type[T], mapping: Callable[[Any], T] | dict[str | int, Callable[[Any], Any] | None]
    ) -> None:
        """Add or overwrite a mapping rule."""
        self._mappings[map_to] = mapping

    def has_mapping(self, map_to: type[Any]) -> bool:
        """Check whether a mapping rule exists for the specified class."""
        return map_to in self._mappings

    @staticmethod
    def _matches_literal(value: Any, literal_type: Any) -> bool:
        return any(
            type(value) is type(literal_value) and value == literal_value
            for literal_value in get_args(literal_type)
        )

    @staticmethod
    def _convert_primitive(
        source: TypeExtractor[Any], target: TypeExtractor[Any]
    ) -> Any:
        try:
            if isinstance(source.instance, target.type):
                return source.instance
        except TypeError:
            # target.type may be a typing construct that cannot be used with isinstance
            pass

        if target.type is UUID and source.type is str:
            try:
                return UUID(source.instance)
            except (ValueError, TypeError):
                raise TypeMismatchError(
                    source_type=source.type, target_type=target.type
                )

        if target.type is Decimal and source.type in {int, float, str}:
            try:
                return Decimal(str(source.instance))
            except (InvalidOperation, ValueError):
                raise TypeMismatchError(
                    source_type=source.type, target_type=target.type
                )

        if target.type is float:
            try:
                return float(source.instance)  # type: ignore
            except (ValueError, TypeError):
                raise TypeMismatchError(
                    source_type=source.type, target_type=target.type
                )

        if source.type is Decimal and target.type is int:
            decimal_value = cast(Decimal, source.instance)
            if decimal_value == decimal_value.to_integral_value():
                return int(decimal_value)
            raise TypeMismatchError(source_type=source.type, target_type=target.type)

        raise TypeMismatchError(source_type=source.type, target_type=target.type)

    @overload
    def map(self, from_instance: None) -> _NullableMapperWrapper: ...

    @overload
    def map(self, from_instance: T) -> _MapperWrapper: ...

    def map(self, from_instance: object) -> _NullableMapperWrapper:
        """Start mapping from an object."""
        if from_instance is None:
            return _NullableMapperWrapper(from_instance, self)
        return _MapperWrapper(from_instance, self)

    def _map_internal(
        self,
        source: TypeExtractor[Any],
        target: TypeExtractor[T],
        _visited_ids_stack: set[int],
    ) -> T:
        """Recursively map a source object to a type or an existing object."""
        custom_mapping: MappingType = (
            self._mappings[target.type] if target.type in self._mappings else {}
        )
        if callable(custom_mapping):
            return custom_mapping(source.instance)  # type: ignore

        if source.instance is None:
            return None  # type: ignore

        target.type = get_type_from_union_type(target.type)

        if source.is_primitive():
            origin = get_origin(target.type)
            if origin is Annotated:
                target.type = get_args(target.type)[0]

            if get_origin(target.type) is Literal:
                if not self._matches_literal(source.instance, target.type):
                    raise TypeMismatchError(
                        source_type=source.type, target_type=target.type
                    )
                return source.instance  # type: ignore
            return self._convert_primitive(source, target)  # type: ignore

        if id(source.instance) in _visited_ids_stack:
            raise CircularReferenceError
        _visited_ids_stack.add(id(source.instance))

        source_accessor = cast(
            InstanceMappingAccessor[Any, Any, Any], self.__get_mapping_accessor(source)
        )
        target_accessor = self.__get_mapping_accessor(target)

        for key, value in source_accessor:
            if key not in target_accessor:
                continue
            if key in custom_mapping:
                if custom_mapping[key] is None:
                    continue
                target_accessor[key] = custom_mapping[key](source.instance)  # type: ignore
                continue

            next_target = TypeExtractor(target_accessor.get_value_type(key))
            next_target.instance = target_accessor[key]
            target_accessor[key] = self._map_internal(
                TypeExtractor(value), next_target, _visited_ids_stack
            )

        for key, mapping in custom_mapping.items():
            if key not in source_accessor and mapping is not None:
                target_accessor[key] = mapping(source.instance)

        _visited_ids_stack.remove(id(source.instance))

        return target_accessor.render()
