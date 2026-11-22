class CircularReferenceError(RecursionError):
    def __init__(self, *args: object) -> None:
        super().__init__("Circular reference during recursive mapping was found")


class UnknownTargetTypeError(TypeError):
    def __init__(self, *args: object, field_type: type) -> None:
        super().__init__(
            f"Not able to deduce target type from source type: {field_type}"
        )


class TypeMismatchError(TypeError):
    def __init__(self, *args: object, source_type: type, target_type: type) -> None:
        super().__init__(f"Not able to convert type {source_type} to {target_type}")
