from typing import Any, get_args, get_origin

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import ColumnProperty, DeclarativeBase, RelationshipProperty

from universal_mapper.accessors.object_accessors.object_accessor import (
    ObjectAccessorMixin,
    ObjectInstanceAccessor,
    ObjectTypeAccessor,
)
from universal_mapper.type_utils import TypeExtractor


class SqlAlchemyObjectMixin[T: DeclarativeBase](ObjectAccessorMixin[T]):
    @classmethod
    def _can_map(cls, target: TypeExtractor[T]) -> bool:
        return inspect(target.type, raiseerr=False) is not None

    def get_fields(self, target_cls: type[T]) -> list[str]:
        inspector = inspect(target_cls)
        return [x.key for x in inspector.attrs]

    def get_field_type(self, target_cls: type[T], field: str) -> Any:
        mapper = inspect(target_cls)
        prop = mapper.attrs.get(field)

        if isinstance(prop, RelationshipProperty):
            related_type = prop.entity.class_
            if prop.uselist:
                return list[related_type]  # type: ignore
            return related_type

        if isinstance(prop, ColumnProperty) and prop.columns:
            try:
                return prop.columns[0].type.python_type
            except (NotImplementedError, AttributeError):
                pass

        # Fallback for edge cases where SQLAlchemy metadata does not expose python type.
        annotation = target_cls.__annotations__.get(field, Any)
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is not None and args:
            # Unwrap wrappers like Mapped[T] -> T.
            return args[0]
        return annotation

    def skip_instance_field(self, instance: T, field: str) -> bool:
        inspector = inspect(instance)

        if field not in inspector.unloaded:
            return False

        # field is unloaded, skip if it's a relationship or a deferred column
        prop = inspector.mapper.attrs.get(field)
        if isinstance(prop, RelationshipProperty):
            return True

        if isinstance(prop, ColumnProperty) and prop.deferred:
            return True

        return False

    def create_instance(self, target_cls: type[T], data: dict[str, Any]) -> T:
        return target_cls(**data)


class SqlAlchemyObjectTypeAccessor[T: DeclarativeBase](
    ObjectTypeAccessor[T], SqlAlchemyObjectMixin[T]
): ...


class SqlAlchemyObjectInstanceAccessor[T: DeclarativeBase](
    ObjectInstanceAccessor[T], SqlAlchemyObjectMixin[T]
): ...
