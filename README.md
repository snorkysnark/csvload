# Easy CSV to SQL loader

This script will run the provided SQL file,
as well as populate the created table with data
based on column annotations

## Example SQL script

```sql
DROP TABLE IF EXISTS foo;
CREATE TABLE foo(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    year INT NOT NULL, --{row[auto()]} same as the column name
    name TEXT NOT NULL, --{row["Person Name"]} has different name in the CSV
    university TEXT NOT NULL, --{"URFU"} just a constant
    group_name TEXT NOT NULL --{arg("group")} console argument
);
```

## Annotations

An column annotation is:
- A comment to the right of the column definition (on the same line)
- The actuall annotation is located inside the curly braces: `{...}`\
  Any text outside the curly braces is ignored
- Represents the right half of a python expression `lambda row: ...`\
  which receives a dictionary and returns the value to be inserted\
  into the corresponding column

#### Special functions:

- `auto()` - returns the corresponding column name
- `arg(name: str)` - retrieves a cli argument by name (see below)

#### Annotation examples:

- `row["Person Name"]` - Named column from CSV
- `row[auto()]` - In the example above, is equivalent to `row["field"]`
- `arg("group")` -\
  For the cli command `csvload.py ... --args group=MEOW`\
  returns the string "MEOW"

## Usage

```
csvload.py db sql data [--args [ARGS ...]] 
```

Where

- `db`
  - is either a [sqlalchemy url](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls),\
  like `sqlite:///result.db`\
  or `postgresql://username:password@host:port/database`
  - or a json file of type:
      ```json
      {
        "drivername": "postgresql",
        "username": "username",
        "password": "password",
        "host": "host",
        "port": 5432
      }
      ```
- `sql` is an annotated SQL file
- `data` is a CSV file
- `args`is a list of key-value pairs, like\
  `--args uni=URFU year=2023`
