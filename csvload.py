from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
import json
import csv

import sqlglot
import sqlparse
import sqlalchemy

from csvload.parser import AnnotatedTable
from csvload.argtypes import keyvalue

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("db", help="sqlalchemy database url or a json file")
    argparser.add_argument("sql", type=Path, help="annotated sql file")
    argparser.add_argument("data", type=Path, help="csv data file")
    argparser.add_argument("--args", nargs="*", action=keyvalue)
    args = argparser.parse_args()

    kwargs = args.args or {}
    print("Args:", kwargs)
    print()

    sql_script = args.sql.read_text()
    parsed_statements = sqlglot.parse(sql_script)
    table_info = AnnotatedTable.from_statements(parsed_statements, kwargs)

    print("Parsed CREATE TABLE statement:")
    pprint(table_info)
    print()

    db_url = (
        sqlalchemy.URL.create(**json.loads(Path(args.db).read_text()))
        if args.db.endswith(".json")
        else args.db
    )

    engine = sqlalchemy.create_engine(db_url, echo=True)
    with engine.connect() as conn:
        # Have to use sqlparse here, not sqlglot,
        # since converting parsed_statements back to string leaves some
        # db-specific keywords (like AUTOINCREMENT) corrupted
        for statement in sqlparse.split(sql_script):
            conn.execute(sqlalchemy.text(statement))

        # Load the created table into sqlalchemy
        engine.echo = False
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=conn, only=[table_info.name], schema=table_info.schema)
        orm_table = metadata.tables[table_info.name]
        engine.echo = True

        with args.data.open() as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                insert = sqlalchemy.insert(orm_table).values(
                    **{
                        col.name: col.get_value(row)
                        for col in table_info.annotated_columns
                    }
                )
                conn.execute(insert)

        conn.commit()
