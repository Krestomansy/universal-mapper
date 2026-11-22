# 4. Core Components

## `ObjectMapper`

The main public class.

- `map(from_instance)`: Initiates the mapping process, returning a `_MapperWrapper` to specify the destination.
- `add_mapping(map_to, mapping)`: Allows registering custom mapping functions for a specific target type. This provides an escape hatch for complex or ambiguous mappings.
- `_map_internal(...)`: The private, recursive workhorse method that performs the deep mapping, using accessors to read from the source and write to the target. It also handles circular reference detection.

## `MappingAccessorFactory`

- `get(target)`: The factory method. It takes a `TypeExtractor` instance and iterates through its internal registry of `TypeMappingAccessor` or `InstanceMappingAccessor` classes. It calls `can_map` on each to find the first one that can handle the target type, then returns an instance of it.

    The order of accessor resolution is important, as the first matching accessor is always used. The factory checks for types in the following order:
    1. **Collections** (`CollectionTypeAccessor` / `CollectionInstanceAccessor`): Reads non-mapping collections by enumerating their elements. When updating an existing collection, the accessor uses indexed reads and writes; lists support this operation.
    2. **Dictionaries** (`DictTypeAccessor` / `DictInstanceAccessor`): Handles `dict` and other `Mapping` types. It iterates using dictionary keys.
    3. **Pydantic Models** (`PydanticObjectTypeAccessor` / `PydanticObjectInstanceAccessor`): Handles Pydantic `BaseModel`s. It uses `model_fields` for introspection.
    4. **SQLAlchemy Models** (`SqlAlchemyObjectTypeAccessor` / `SqlAlchemyObjectInstanceAccessor`): Handles SQLAlchemy declarative models. It uses the SQLAlchemy `inspect` utility. A key feature here is its ability to skip unloaded relationships to prevent `DetachedInstanceError`.
    5. **Default Python Objects** (`DefaultObjectTypeAccessor` / `DefaultObjectInstanceAccessor`): Handles plain Python objects. It uses `__init__` annotations to discover fields.

## `MappingAccessor`

The abstract base class for all accessors. It defines the common interface for:

- Checking if a key/field/index exists (`__contains__`).
- Getting a value (`__getitem__`).
- Setting a value (`__setitem__`).
- Determining the type of a value at a given key (`get_value_type`).
- Constructing/returning the final object (`render`).

## `TypeExtractor`

A utility class that wraps a type or an instance to provide a consistent API for type introspection, such as getting the origin type (`list` from `list[int]`) or checking if a type is a primitive.
