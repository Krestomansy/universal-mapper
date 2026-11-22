# 5. Functionality and Usage

This section provides practical examples of `ObjectMapper`'s features based on the library's test suite.

## Automatic Mapping

The mapper can automatically map data between objects with matching field names, including nested objects and collections. Pydantic and SQLAlchemy models are supported when their respective dependencies are installed.

### Simple Objects

You can map a source object to a target class. The mapper will create a new instance of the target class and populate its fields.

```python
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from universal_mapper import ObjectMapper


# Define source and target classes
class UserDto(BaseModel):
    id: str
    name: str


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]


# --- Usage ---
mapper = ObjectMapper()
user_dto = UserDto(id="user1", name="John Doe")

# Map from Pydantic DTO to SQLAlchemy ORM
user_orm = mapper.map(user_dto).to(UserOrm)

assert user_orm.id == "user1"
assert user_orm.name == "John Doe"
```

### Collections and Dictionaries

The mapper recursively handles collections such as lists, homogeneous tuples, and dictionaries. The target collection specifies its element type; dictionaries specify their key and value types. The following examples continue from the preceding example.

```python
# Map a list of objects
users_dto_list = [UserDto(id="u1", name="John"), UserDto(id="u2", name="Jane")]
users_orm_list = mapper.map(users_dto_list).to(list[UserOrm])
# -> [UserOrm(id='u1', ...), UserOrm(id='u2', ...)]

# Map a dictionary of objects
users_dto_dict = {"A": UserDto(id="u1", name="John")}
users_orm_dict = mapper.map(users_dto_dict).to(dict[str, UserOrm])
# -> {'A': UserOrm(id='u1', ...)}
```

## Merging / Updating Objects

You can map data onto an *existing* instance, for example to apply updates from a DTO to an ORM model. The mapper processes fields exposed by the source and accepted by the destination accessor. For Pydantic instances, a field with an implicit default of `None` is skipped; an explicitly set `None` is included. The same field-availability check applies to an existing Pydantic destination.

```python
class UserUpdateDto(BaseModel):
    name: str | None = None


existing_user_orm = UserOrm(id="user1", name="John Doe")
update_dto = UserUpdateDto(name="Jonathan Doe")

# Merge the update DTO into the existing ORM instance
mapper.map(update_dto).to(existing_user_orm)

assert existing_user_orm.id == "user1"
assert existing_user_orm.name == "Jonathan Doe"
```

This works recursively. When merging lists, it updates elements at corresponding indices within the destination's existing length, leaving trailing destination elements unchanged.

## Custom Mapping Rules

For more complex scenarios, such as when field names differ or data requires transformation, you can define custom mapping rules using `add_mapping`.

### Field-Specific Rules (lambda)

Use a dictionary of lambdas to define rules for specific fields. This is useful for combining, splitting, or transforming data.

```python
class User:
    def __init__(self, id: str, first_name: str, last_name: str):
        self.id, self.first_name, self.last_name = id, first_name, last_name


class ModifiedUserDto(BaseModel):
    id: str
    name: str


mapper = ObjectMapper()
mapper.add_mapping(
    ModifiedUserDto,
    # Rule to combine first_name and last_name into a single 'name' field
    {"name": lambda user: f"{user.first_name} {user.last_name}"},
)

user_obj = User(id="user1", first_name="John", last_name="Doe")
result_dto = mapper.map(user_obj).to(ModifiedUserDto)

# result_dto is ModifiedUserDto(id='user1', name='John Doe')
```

If a custom mapping dictionary contains a field mapped to `None`, that field will be explicitly skipped during the mapping process. This allows you to prevent certain fields from being mapped even if they exist in the source.

```python
class NameDto(BaseModel):
    id: str
    first_name: str
    last_name: str


class NameUpdateDto(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

mapper = ObjectMapper()
# Skip 'last_name' in the mapping to NameDto
mapper.add_mapping(NameDto, mapping={"last_name": None})

existing_user = NameDto(id="user1", first_name="John", last_name="Doe")
update_data = NameUpdateDto(
    first_name="Jonathan", last_name="NewLastName"
)  # last_name will be ignored due to the rule

# Act: Merge update_data into existing_user
mapper.map(update_data).to(existing_user)

# Assert: last_name remains unchanged, first_name is updated
assert existing_user.first_name == "Jonathan"
assert existing_user.last_name == "Doe"
```

### Type-Specific Rules (function)

For a complete override of the mapping logic for a given type, you can provide a single function.

```python
def map_user_to_dto(user: UserOrm) -> UserDto:
    # Custom logic to create the DTO
    return UserDto(id=f"processed-{user.id}", name=user.name.upper())


mapper.add_mapping(UserDto, map_user_to_dto)

user_orm = UserOrm(id="user1", name="John Doe")
result_dto = mapper.map(user_orm).to(UserDto)

# result_dto is UserDto(id='processed-user1', name='JOHN DOE')
```
