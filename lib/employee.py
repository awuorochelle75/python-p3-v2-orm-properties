from __init__ import CURSOR, CONN
from department import Department


class Employee:

    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name  # uses setter for validation
        self.job_title = job_title  # uses setter for validation
        self.department_id = department_id  # uses setter for validation

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department {self.department_id}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and value.strip():
            self._name = value.strip()
        else:
            raise ValueError("Employee name must be a non-empty string.")

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if isinstance(value, str) and value.strip():
            self._job_title = value.strip()
        else:
            raise ValueError("Job title must be a non-empty string.")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer.")
        if value not in Department.all:
            raise ValueError("Department ID must reference an existing department.")
        self._department_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            );
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        self.id = CURSOR.lastrowid
        CONN.commit()
        Employee.all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        if self.id is None:
            raise ValueError("Cannot update an Employee without an ID.")
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        if self.id is None:
            raise ValueError("Cannot delete an Employee without an ID.")
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Remove from cache and reset id to None
        Employee.all.pop(self.id, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        emp = cls(row[1], row[2], row[3], row[0])
        Employee.all[emp.id] = emp
        return emp

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_name(cls, name):
        # Check cache first (return first match if any)
        for emp in cls.all.values():
            if emp.name == name:
                return emp

        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_id(cls, id):
        # Return cached instance if exists
        if id in cls.all:
            return cls.all[id]
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
