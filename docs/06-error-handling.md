# 6. Error Handling

The mapper is designed to fail predictably when it encounters an ambiguous or impossible mapping scenario.

The examples below continue from the models and imports in [Functionality and Usage](05-usage.md).

## `CircularReferenceError`

Raised to prevent infinite loops when objects contain references to each other.

```python
from universal_mapper import ObjectMapper
from universal_mapper.exceptions import CircularReferenceError


class Node:
    def __init__(self, child: "Node | None" = None):
        self.child = child


node1 = Node()
node2 = Node(child=node1)
node1.child = node2  # Creates a circular reference
mapper = ObjectMapper()

try:
    mapper.map(node1).to(Node)
except CircularReferenceError as e:
    print(e)
```

## `UnknownTargetTypeError`

Raised when the target type is ambiguous. This commonly occurs with `Union` types that have multiple non-None members, or with generic collections that are missing type arguments.

```python
from universal_mapper.exceptions import UnknownTargetTypeError


class AmbiguousDto(BaseModel):
    field1: list  # Missing type args like list[str]
    field2: str | int  # Ambiguous union


try:
    # This will fail because the type of field1's items cannot be inferred.
    mapper.map(AmbiguousDto(field1=[1, 2], field2=1)).to(AmbiguousDto)
except UnknownTargetTypeError as e:
    print(e)
```

## `TypeMismatchError`

Raised when trying to map incompatible primitive types without a custom rule.

```python
from universal_mapper.exceptions import TypeMismatchError


try:
    mapper.map("hello world").to(int)
except TypeMismatchError as e:
    print(e)
```
