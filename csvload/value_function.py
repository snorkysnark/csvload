from typing import Any, Callable


class CompiledFunction:
    def __init__(self, source: str, compiled: Callable):
        self.source = source
        self.compiled = compiled

    def __str__(self) -> str:
        return self.source

    def __repr__(self) -> str:
        return self.source

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.compiled(*args, **kwds)


class Environment:
    def __init__(self, args: dict):
        self.args = args

    def get_arg(self, arg: str):
        return self.args.get(arg)

    def create_lambda_from_annotation(self, annotation: str, field: str):
        def get_field():
            return field

        source = "lambda row: " + annotation

        return CompiledFunction(
            source, eval(source, {}, {"auto": get_field, "arg": self.get_arg})
        )
