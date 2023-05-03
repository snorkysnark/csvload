import re
from dataclasses import dataclass
from typing import Any, Callable, Optional
import sqlglot
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


def find_text_in_braces(comment: str):
    """Find the first string in the outermost curly braces"""
    first_opening_brace = comment.find("{")
    if first_opening_brace == -1:
        return None

    level = 1

    for i in range(first_opening_brace + 1, len(comment)):
        if comment[i] == "{":
            level += 1
        elif comment[i] == "}":
            level -= 1

        if level == 0:
            return comment[first_opening_brace + 1 : i]


def find_annotation(expression: Expression):
    for comment in find_all_comments(expression):
        annotation = find_text_in_braces(comment)
        if annotation:
            return annotation


@dataclass
class AnnotatedColumn:
    name: str
    get_value: Callable[[dict], Any]

    @staticmethod
    def from_expression(expression: Expression, env: Environment):
        if expression.key != "columndef":
            raise RuntimeError(f"Expected columndef expression, found {expression.key}")

        name = expression.args["this"].args["this"]
        annotation = find_annotation(expression)
        get_value = (
            env.create_lambda_from_annotation(annotation, name) if annotation else None
        )

        if get_value:
            return AnnotatedColumn(name, get_value)


@dataclass
class AnnotatedTable:
    name: str
    schema: Optional[str]
    annotated_columns: list[AnnotatedColumn]

    @staticmethod
    def from_statements(statements: list[Optional[Expression]], args: dict):
        create_table = next(expr for expr in statements if is_create_table(expr))
        if not create_table:
            raise RuntimeError("CREATE TABLE statement not found")

        table_expr = create_table.args["this"].args["this"]
        name = table_expr.args["this"].args["this"]
        schema_expr = table_expr.args["db"]
        schema = schema_expr.args["this"] if schema_expr else None

        columndefs = create_table.args["this"].args["expressions"]

        env = Environment(args)
        annotated_columns = []

        for coldef in columndefs:
            parsed_column = AnnotatedColumn.from_expression(coldef, env)
            if parsed_column:
                annotated_columns.append(parsed_column)

        return AnnotatedTable(name, schema, annotated_columns)


def detect_dialect(sql: str):
    match = re.search(r"^--dialect=(\w*)$", sql, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        raise RuntimeError("The script must contain a comment of type '--dialect=...'")
