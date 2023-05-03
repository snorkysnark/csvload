DROP TABLE IF EXISTS foo;
CREATE TABLE foo(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    year INT NOT NULL, --{row[auto()]}
    name TEXT NOT NULL, --{row["person_name"]}
    university TEXT NOT NULL, --{"URFU"}
    group_name TEXT NOT NULL --{arg("group")}
);
