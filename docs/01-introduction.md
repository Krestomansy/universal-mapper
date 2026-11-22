# 1. Introduction

The `universal_mapper` package provides `ObjectMapper` for mapping data between supported Python objects, collections, dictionaries, Pydantic models, and SQLAlchemy declarative models. For plain Python objects, it discovers fields from annotated `__init__` parameters.

The core functionality allows for deep, recursive mapping between objects, with support for custom mapping logic and robust error handling for issues like circular references.

The primary API is designed to be fluent and intuitive:

```python
from universal_mapper import ObjectMapper


class Source:
    def __init__(self, name: str):
        self.name = name


class Target:
    def __init__(self, name: str):
        self.name = name


mapper = ObjectMapper()
mapped_object = mapper.map(Source("Ada")).to(Target)
assert mapped_object.name == "Ada"
```

## Requirements and installation

The package requires Python 3.12 or later. Install the base package with:

```bash
pip install universal-mapper
```

Pydantic and SQLAlchemy integrations are optional. Install either or both extras as needed:

```bash
pip install "universal-mapper[pydantic]"
pip install "universal-mapper[sqlalchemy]"
pip install "universal-mapper[pydantic,sqlalchemy]"
```

The integrations require Pydantic 2 or later and SQLAlchemy 2 or later. They are enabled when the respective libraries are installed, including when those libraries were installed separately.
