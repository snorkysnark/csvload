from pathlib import Path
from typing import Optional
import sqlglot
from sqlglot.expressions import Expression


def is_create_table(expression: Optional[Expression]):
    return (
        expression
        and expression.key == "create"
        and expression.args["kind"].lower() == "table"
    )


expressions = sqlglot.parse(Path("./example.sql").read_text())
create_table = next(expr for expr in expressions if is_create_table(expr))
assert create_table

columns = create_table.args["this"].args["expressions"]

print(create_table)
