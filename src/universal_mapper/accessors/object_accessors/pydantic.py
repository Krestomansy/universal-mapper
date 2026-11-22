from typing import Any

from pydantic import BaseModel

from universal_mapper.accessors.object_accessors.object_accessor import (
    ObjectAccessorMixin,
    ObjectInstanceAccessor,
    ObjectTypeAccessor,
)
from universal_mapper.type_utils import TypeExtractor


class PydanticObjectMixin[T: BaseModel](ObjectAccessorMixin[T]):
    @classmethod
    def _can_map(cls, target: TypeExtractor[T]) -> bool:
        return issubclass(target.type, BaseModel)

    def get_fields(self, target_cls: type[T]) -> list[str]:
        return list(target_cls.model_fields.keys())

    def get_field_type(self, target_cls: type[T], field: str) -> Any:
        return target_cls.model_fields[field].annotation

    def skip_instance_field(self, instance: T, field: str) -> bool:
        if field not in instance.model_fields_set and getattr(instance, field) is None:
            return True
        return False

    def create_instance(self, target_cls: type[T], data: dict[str, Any]) -> T:
        return target_cls(**data)


class PydanticObjectTypeAccessor[T: BaseModel](
    ObjectTypeAccessor[T], PydanticObjectMixin[T]
): ...


class PydanticObjectInstanceAccessor[T: BaseModel](
    ObjectInstanceAccessor[T], PydanticObjectMixin[T]
): ...
