from argparse import ArgumentParser
from pathlib import Path

import sqlglot
import sqlparse
import sqlalchemy

from csvload.parser import AnnotatedTable

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("db", help="sqlalchemy database url")
    argparser.add_argument("sql", type=Path, help="annotated sql file")
    # argparser.add_argument("data", type=Path, help="csv data file")
    args = argparser.parse_args()

    sql_script = args.sql.read_text()
    parsed_statements = sqlglot.parse(sql_script)
    table_info = AnnotatedTable.from_statements(parsed_statements, {"group": "egg_irl"})

    engine = sqlalchemy.create_engine(args.db, echo=True)
    with engine.connect() as conn:
        # Have to use sqlparse here, not sqlglot,
        # since converting parsed_statements back to string leaves some
        # db-specific keywords (like AUTOINCREMENT) corrupted
        for statement in sqlparse.split(sql_script):
            conn.execute(sqlalchemy.text(statement))
