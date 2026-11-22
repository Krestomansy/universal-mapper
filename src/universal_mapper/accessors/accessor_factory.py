from typing import Any

from universal_mapper.accessors.abstract_base import (
    InstanceMappingAccessor,
    MappingAccessor,
    TypeMappingAccessor,
)
from universal_mapper.accessors.collection import (
    CollectionInstanceAccessor,
    CollectionTypeAccessor,
)
from universal_mapper.accessors.dict import DictInstanceAccessor, DictTypeAccessor
from universal_mapper.accessors.object_accessors import (
    DefaultObjectInstanceAccessor,
    DefaultObjectTypeAccessor,
)
from universal_mapper.type_utils import TypeExtractor

_type_accessors: list[type[TypeMappingAccessor[Any, Any, Any]]] = []
_instance_accessors: list[type[InstanceMappingAccessor[Any, Any, Any]]] = []

try:
    from universal_mapper.accessors.object_accessors.pydantic import (
        PydanticObjectInstanceAccessor,
        PydanticObjectTypeAccessor,
    )
except ModuleNotFoundError as exc:
    if exc.name != "pydantic":
        raise
else:
    _type_accessors.append(PydanticObjectTypeAccessor)
    _instance_accessors.append(PydanticObjectInstanceAccessor)

try:
    from universal_mapper.accessors.object_accessors.sqlalchemy import (
        SqlAlchemyObjectInstanceAccessor,
        SqlAlchemyObjectTypeAccessor,
    )
except ModuleNotFoundError as exc:
    if exc.name != "sqlalchemy":
        raise
else:
    _type_accessors.append(SqlAlchemyObjectTypeAccessor)
    _instance_accessors.append(SqlAlchemyObjectInstanceAccessor)


class MappingAccessorFactory:
    __type_iterators_registry: list[type[TypeMappingAccessor[Any, Any, Any]]] = [
        CollectionTypeAccessor,
        DictTypeAccessor,
        *_type_accessors,
        DefaultObjectTypeAccessor,
    ]

    __instance_iterators_registry: list[type[InstanceMappingAccessor[Any, Any, Any]]] = [
        CollectionInstanceAccessor,
        DictInstanceAccessor,
        *_instance_accessors,
        DefaultObjectInstanceAccessor,
    ]

    @classmethod
    def get[T](cls, target: TypeExtractor[T]) -> MappingAccessor[T, Any, Any]:
        if target.instance is None:
            return cls.get_type_accessor(target)
        else:
            return cls.get_instance_accessor(target)

    @classmethod
    def get_type_accessor[T](cls, target: TypeExtractor[T]) -> TypeMappingAccessor[T, Any, Any]:
        for iterator_type in cls.__type_iterators_registry:
            if iterator_type.can_map(target):
                return iterator_type(target.type)
        raise NotImplementedError(f"Mapping iterator for type {target.type} not found")

    @classmethod
    def get_instance_accessor[T](cls, target: TypeExtractor[T]) -> InstanceMappingAccessor[T, Any, Any]:
        for iterator_type in cls.__instance_iterators_registry:
            if iterator_type.can_map(target):
                return iterator_type(target.type, target.instance)
        raise NotImplementedError(f"Mapping iterator for instance of type {target.type} not found")
