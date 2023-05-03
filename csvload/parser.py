from dataclasses import dataclass
from typing import Any, Callable, Optional
from sqlglot.expressions import Expression


def is_create_table(expression: Optional[Expression]):
    return (
        expression
        and expression.key == "create"
        and expression.args["kind"].lower() == "table"
    )


@dataclass
class AnnotatedColumn:
    name: str
    get_value: Optional[Callable[[dict], Any]]

    @staticmethod
    def from_expression(expression: Expression, args: dict):
        if expression.key != "columndef":
            raise RuntimeError(f"Expected columndef expression, found {expression.key}")

        name = expression.args["this"].args["this"]


@dataclass
class AnnotatedTable:
    table: str
    schema: Optional[str]
    columns: list[AnnotatedColumn]

    @staticmethod
    def from_expressions(expressions: list[Optional[Expression]]):
        create_table = next(expr for expr in expressions if is_create_table(expr))
        if not create_table:
            raise RuntimeError("CREATE TABLE expression not found")

        table_expr = create_table.args["this"].args["this"]
        table = table_expr.args["this"].args["this"]
        schema_expr = table_expr.args["db"]
        schema = schema_expr.args["this"] if schema_expr else None

        columndefs = create_table.args["this"].args["expressions"]

        return AnnotatedTable(table=table, schema=schema, columns=columndefs)
