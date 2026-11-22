from typing import Any, cast, get_type_hints

from universal_mapper.accessors.object_accessors.object_accessor import (
    ObjectAccessorMixin,
    ObjectInstanceAccessor,
    ObjectTypeAccessor,
)
from universal_mapper.type_utils import TypeExtractor

_IGNORED_FIELDS = ("return", "args", "kwargs")


class DefaultObjectMixin[T: object](ObjectAccessorMixin[T]):
    @classmethod
    def _can_map(cls, target: TypeExtractor[T]) -> bool:
        # supports only objects with defined constructors
        try:
            annotations = target.type.__init__.__annotations__
        except AttributeError:
            return False
        return any(field not in _IGNORED_FIELDS for field in annotations)

    def get_fields(self, target_cls: type[T]) -> list[str]:
        result = []
        for field in target_cls.__init__.__annotations__.keys():
            if field not in _IGNORED_FIELDS:
                result.append(field)
        return result

    def get_field_type(self, target_cls: type[T], field: str) -> Any:
        type_hints = get_type_hints(target_cls.__init__)
        return type_hints.get(field, Any)

    def skip_instance_field(self, instance: T, field: str) -> bool:
        return not hasattr(instance, field)

    def create_instance(self, target_cls: type[T], data: dict[str, Any]) -> T:
        return cast(target_cls, target_cls(**data))  # type: ignore


class DefaultObjectTypeAccessor[T: object](
    ObjectTypeAccessor[T], DefaultObjectMixin[T]
): ...


class DefaultObjectInstanceAccessor[T: object](
    ObjectInstanceAccessor[T], DefaultObjectMixin[T]
): ...
