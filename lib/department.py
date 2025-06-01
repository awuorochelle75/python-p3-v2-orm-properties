# lib/department.py
from __init__ import CURSOR, CONN

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name  # will trigger setter validation
        self.location = location  # will trigger setter validation

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    # name property with validation
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        if len(value.strip()) == 0:
            raise ValueError("name must not be empty")
        self._name = value

    # location property with validation
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("location must be a string")
        if len(value.strip()) == 0:
            raise ValueError("location must not be empty")
        self._location = value

    @classmethod
    def create_table(cls):
        """Create the departments table if it doesn't exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the departments table."""
        sql = "DROP TABLE IF EXISTS departments;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert the current department into the database."""
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update this department in the database."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete this department from the database and internal store."""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, location):
        """Create and save a new department."""
        department = cls(name, location)
        department.save()
        return department

    @classmethod
    def instance_from_db(cls, row):
        """Return a department object from a DB row."""
        department = cls.all.get(row[0])
        if department:
            # update existing object attributes if changed
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2], row[0])
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        """Get all departments."""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Find a department by its ID."""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find a department by its name."""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def employees(self):
        """Get all employees in this department."""
        from employee import Employee  # Delayed import to avoid circular import
        sql = "SELECT * FROM employees WHERE department_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows]
