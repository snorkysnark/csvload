from dataclasses import dataclass
from typing import Any, Callable, Optional
from sqlglot.expressions import Expression

from .value_function import Environment


def is_create_table(statement: Optional[Expression]):
    return (
        statement
        and statement.key == "create"
        and statement.args["kind"].lower() == "table"
    )


def find_all_comments(root: Expression):
    for expr, parent, key in root.walk():
        if expr.comments:
            yield from expr.comments


def find_annotation(expression: Expression):
    for comment in find_all_comments(expression):
        if comment.startswith("{") and comment.endswith("}"):
            return comment[1:-1]


@dataclass
class AnnotatedColumn:
    name: str
    get_value: Optional[Callable[[dict], Any]]

    @staticmethod
    def from_expression(expression: Expression, env: Environment):
        if expression.key != "columndef":
            raise RuntimeError(f"Expected columndef expression, found {expression.key}")

        name = expression.args["this"].args["this"]
        annotation = find_annotation(expression)
        get_value = (
            env.create_lambda_from_annotation(annotation, name) if annotation else None
        )

        return AnnotatedColumn(name, get_value)


@dataclass
class AnnotatedTable:
    table: str
    schema: Optional[str]
    columns: list[AnnotatedColumn]

    @staticmethod
    def from_statements(statements: list[Optional[Expression]], args: dict):
        create_table = next(expr for expr in statements if is_create_table(expr))
        if not create_table:
            raise RuntimeError("CREATE TABLE statement not found")

        table_expr = create_table.args["this"].args["this"]
        table = table_expr.args["this"].args["this"]
        schema_expr = table_expr.args["db"]
        schema = schema_expr.args["this"] if schema_expr else None

        columndefs = create_table.args["this"].args["expressions"]

        env = Environment(args)
        parsed_columns = list(
            map(lambda coldef: AnnotatedColumn.from_expression(coldef, env), columndefs)
        )

        return AnnotatedTable(table=table, schema=schema, columns=parsed_columns)
