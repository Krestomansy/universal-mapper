# Universal Mapper

Universal Mapper is a Python library for mapping data between objects, models, and collections. It supports nested structures, updates to existing objects, and custom mapping rules.

The library requires Python 3.12 or later. It supports ordinary Python objects, dictionaries, and collections, with optional integrations for Pydantic and SQLAlchemy when those libraries are installed.

## License

Distributed under the [MIT License](LICENSE).

## Versions

### 1.0.0 — Unreleased

- Initial version with recursive mapping, object updates, and custom mapping rules.
- Optional support for Pydantic and SQLAlchemy models.

## Usage

### Map an object

For ordinary Python classes, fields are discovered from annotated `__init__` parameters.

```python
from universal_mapper import ObjectMapper


class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class UserDto:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


mapper = ObjectMapper()
user = User(id=1, name="Ada")
dto = mapper.map(user).to(UserDto)

assert (dto.id, dto.name) == (1, "Ada")
```

### Update an existing object

The mapper can update an existing object. This example continues from the previous one.

```python
updated = User(id=1, name="Grace")
mapper.map(updated).to(dto)

assert dto.name == "Grace"
```

### Define a custom mapping rule

Use a mapping rule to calculate a target field from the source object.

```python
from universal_mapper import ObjectMapper


class Person:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


class PersonDto:
    def __init__(self, full_name: str):
        self.full_name = full_name


mapper = ObjectMapper()
mapper.add_mapping(
    PersonDto,
    {"full_name": lambda person: f"{person.first_name} {person.last_name}"},
)

dto = mapper.map(Person("Ada", "Lovelace")).to(PersonDto)
assert dto.full_name == "Ada Lovelace"
```

### Skip a field

Set a field's mapping rule to `None` to leave that field unchanged when updating an object. This example continues from the first usage example.

```python
mapper = ObjectMapper()
mapper.add_mapping(UserDto, {"id": None})

existing = UserDto(id=1, name="Ada")
mapper.map(User(id=2, name="Grace")).to(existing)

assert (existing.id, existing.name) == (1, "Grace")
```

### Map with a function

Register a function to define the complete mapping for a target type.

```python
from universal_mapper import ObjectMapper


class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius


class TemperatureDto:
    def __init__(self, fahrenheit: float):
        self.fahrenheit = fahrenheit


def to_fahrenheit(source: Temperature) -> TemperatureDto:
    return TemperatureDto(fahrenheit=source.celsius * 9 / 5 + 32)


mapper = ObjectMapper()
mapper.add_mapping(TemperatureDto, to_fahrenheit)

result = mapper.map(Temperature(20.0)).to(TemperatureDto)
assert result.fahrenheit == 68.0
```

See the [documentation](docs/README.md) for more examples and details about integrations, collections, and error handling.

## Inspiration

This project was inspired by [marazt/object-mapper](https://github.com/marazt/object-mapper).

## AI assistance

AI tools were used to assist with documentation, testing, and parts of the implementation. All changes are reviewed by the project maintainer.
