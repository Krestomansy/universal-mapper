from datetime import date, datetime
from decimal import Decimal
from types import UnionType
from typing import Any, Union, get_args, get_origin
from uuid import UUID

from universal_mapper.exceptions import UnknownTargetTypeError


class TypeExtractor[T]:
    __PRIMITIVE_BASE_TYPES = (
        int,
        float,
        complex,
        Decimal,
        str,
        bytes,
        bytearray,
        bool,
        date,
        datetime,
        UUID,
    )

    def __init__(self, type_or_instance: type[T] | T):
        self.type: type[T]
        self.instance: T | None = None
        # If it's a class (like `UserDto`) or a generic alias (like `list[UserDto]`)
        if (
            isinstance(type_or_instance, type)
            or get_origin(type_or_instance) is not None
        ):
            self.type = type_or_instance  # type: ignore [assignment]
        # If it's an instance of a class (like `UserDto(...)`)
        else:
            self.type = type(type_or_instance)
            self.instance = type_or_instance

    def is_primitive(self) -> bool:
        """Check whether the object or type is primitive."""
        if self.instance is not None:
            return isinstance(self.instance, self.__PRIMITIVE_BASE_TYPES)

        try:
            return issubclass(self.type, self.__PRIMITIVE_BASE_TYPES)
        except TypeError:
            return False

    def get_origin(self) -> type:
        """
        Get the origin type from a composite type.
        For example, return `list` for `list[UserDto]`.
        """
        if get_origin(self.type) is not None:
            return get_origin(self.type)  # type: ignore
        else:
            return self.type


def get_type_from_composite_type(target_type: Any) -> Any:
    """
    Get the element type from a collection type.
    For example, return `UserDto` for `list[UserDto]`.
    """
    origin = get_origin(target_type)
    args = get_args(target_type)

    if origin is tuple and len(args) > 1 and args[1] is not ...:
        raise NotImplementedError("Heterogenous tuples are not supported")
    if len(args) == 1 or origin is tuple and args[1] is ...:
        return args[0]
    if origin is dict:
        return args[1]

    raise UnknownTargetTypeError(field_type=target_type)


def get_type_from_union_type(target_type: Any) -> Any:
    """
    Recursively extract a type from a union.
    Raise an error if a union contains more than one non-None type.
    """
    origin = get_origin(target_type)
    args = get_args(target_type)

    if origin is Union or origin is UnionType:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return get_type_from_union_type(non_none_args[0])
        else:
            raise UnknownTargetTypeError(field_type=target_type)

    return target_type
