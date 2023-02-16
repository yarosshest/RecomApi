CREATE TABLE ObjectType (
    name TEXT PRIMARY KEY,
    parent TEXT,
    FOREIGN KEY (parent) REFERENCES ObjectType(name)
);


CREATE TABLE Object (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    image TEXT NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (type) REFERENCES ObjectType(name)
);

CREATE TABLE ObjectTextProperty (
    id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES Object(id)
);

CREATE TABLE ObjectIntegerProperty (
    id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY (object_id) REFERENCES Object(id)
);
