# 3. Class Hierarchy

The power of the module comes from its composable and layered class structure, primarily revolving around the `MappingAccessor` abstract base class.

## `MappingAccessor` Inheritance

There are two main branches of accessors:

1. **`TypeMappingAccessor`**: Used when mapping *to a type* (creating a new instance). It builds up the data internally and uses a `render()` method to create the final object.
2. **`InstanceMappingAccessor`**: Used when mapping *from an instance* (reading data) or updating an existing instance. It reads data from the provided object instance.

This diagram shows the main branches of the accessor hierarchy.

```mermaid
classDiagram
    direction RL
    class MappingAccessor {
        <<Interface>>
        +can_map(target) bool
        +get_value_type(key) type
        +__contains__(key) bool
        +__getitem__(key) any
        +__setitem__(key, value)
        +render() T
    }

    class TypeMappingAccessor {
        <<Abstract>>
    }

    class InstanceMappingAccessor {
        <<Abstract>>
        +__iter__() Iterator
    }

    MappingAccessor <|-- TypeMappingAccessor
    MappingAccessor <|-- InstanceMappingAccessor

    TypeMappingAccessor <|-- CollectionTypeAccessor
    TypeMappingAccessor <|-- DictTypeAccessor
    TypeMappingAccessor <|-- ObjectTypeAccessor

    InstanceMappingAccessor <|-- CollectionInstanceAccessor
    InstanceMappingAccessor <|-- DictInstanceAccessor
    InstanceMappingAccessor <|-- ObjectInstanceAccessor
```

## `ObjectAccessor` Specialization (Template Method)

For handling object-like structures, a specialized mixin-based approach is used. The `ObjectAccessorMixin` defines the interface, and concrete mixins implement it for different object frameworks.

```mermaid
classDiagram
  direction LR

  class ObjectAccessorMixin {
    <<Interface>>
    #get_fields()
    #get_field_type()
    #create_instance()
  }

  class ObjectTypeAccessor {
    <<Base Class>>
    +render()
  }

  class PydanticObjectMixin {
    <<Implementation>>
    #get_fields()
    #get_field_type()
    #create_instance()
  }
  ObjectAccessorMixin <|-- PydanticObjectMixin

  class PydanticObjectTypeAccessor {
    ...
  }

  ObjectTypeAccessor <|-- PydanticObjectTypeAccessor
  PydanticObjectMixin <|-- PydanticObjectTypeAccessor

  note "The same pattern applies to DefaultObject and SqlAlchemyObject accessors, and for InstanceAccessors."

```
