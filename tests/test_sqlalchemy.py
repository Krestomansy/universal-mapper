import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from universal_mapper import ObjectMapper


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


def test_mapping_sqlalchemy_without_pydantic() -> None:
    mapper = ObjectMapper()
    user = mapper.map({"id": 1, "name": "Ada"}).to(User)
    assert (user.id, user.name) == (1, "Ada")
    copied = mapper.map(user).to(User)
    assert (copied.id, copied.name) == (1, "Ada")
