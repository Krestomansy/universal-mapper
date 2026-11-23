from typing import assert_type

from universal_mapper import ObjectMapper


class Target:
    pass


def check_types(optional_source: int | None) -> None:
    """Check inferred result types and validation of complete mapping functions."""
    mapper = ObjectMapper()
    target = Target()
    assert_type(mapper.map(1).to(Target), Target)
    assert_type(mapper.map(1).to(target), Target)
    assert_type(mapper.map([1]).to(list[int]), list[int])
    assert_type(mapper.map(None).to(Target), Target | None)
    assert_type(mapper.map(optional_source).to(Target), Target | None)

    def valid_mapping(_source: int) -> Target:
        return Target()

    def invalid_mapping(source: int) -> str:
        return str(source)

    mapper.add_mapping(Target, valid_mapping)
    mapper.add_mapping(Target, invalid_mapping)  # type: ignore[arg-type]
    mapper.add_mapping(Target, {"field": lambda source: source})
