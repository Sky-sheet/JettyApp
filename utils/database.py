# -*- coding: utf-8 -*-
"""مدیریت پایگاه داده SQLite"""

import sqlite3
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict


def hash_password(password: str, salt: str = "JettyAllowance2024") -> str:
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    if hashed == plain:  # سازگاری با نسخه قدیمی
        return True
    return hash_password(plain) == hashed


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            c = conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )
            """)

            # کاربر پیش‌فرض admin / admin
            c.execute(
                "INSERT OR IGNORE INTO users VALUES (?, ?)",
                ("admin", hash_password("admin")),
            )

            c.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    personnel_number TEXT NOT NULL,
                    employment_type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    jetty_type TEXT NOT NULL
                )
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_employee_unique
                ON employees (personnel_number, date, jetty_type)
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS default_employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    personnel_number TEXT NOT NULL UNIQUE,
                    employment_type TEXT NOT NULL,
                    photo_path TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS task_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    jetty_type TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS delete_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    delete_date TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    deleted_file TEXT NOT NULL
                )
            """)
            conn.commit()

    # ---------- کاربران ----------
    def check_login(self, username: str, password: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT password FROM users WHERE username=?", (username,)
            ).fetchone()
        return bool(row and verify_password(password, row[0]))

    def get_users(self) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute("SELECT username, password FROM users").fetchall()

    def add_user(self, username: str, password: str) -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users VALUES (?, ?)",
                    (username, hash_password(password))
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_user(self, old_username: str, new_username: str, new_password: str = None) -> bool:
        try:
            with self._connect() as conn:
                if new_password:
                    conn.execute(
                        "UPDATE users SET username=?, password=? WHERE username=?",
                        (new_username, hash_password(new_password), old_username)
                    )
                else:
                    conn.execute(
                        "UPDATE users SET username=? WHERE username=?",
                        (new_username, old_username)
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def delete_user(self, username: str) -> bool:
        if username == "Administrator":
            return False
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
        return True

    # ---------- کارمندان پیش‌فرض ----------
    def get_default_employees(self) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT full_name, personnel_number, employment_type, photo_path FROM default_employees"
            ).fetchall()

    def get_employee_by_personnel(self, pnum: str) -> Optional[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT full_name, personnel_number, employment_type, photo_path "
                "FROM default_employees WHERE personnel_number=?",
                (pnum,)
            ).fetchone()

    def add_default_employee(self, name: str, pnum: str, emp_type: str, photo: str = None) -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO default_employees (full_name, personnel_number, employment_type, photo_path) "
                    "VALUES (?, ?, ?, ?)",
                    (name, pnum, emp_type, photo)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_default_employee(self, old_pnum: str, name: str, pnum: str, emp_type: str) -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE default_employees SET full_name=?, personnel_number=?, employment_type=? "
                    "WHERE personnel_number=?",
                    (name, pnum, emp_type, old_pnum)
                )
                conn.commit()
            return True
        except Exception:
            return False

    def delete_default_employee(self, pnum: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM default_employees WHERE personnel_number=?", (pnum,))
            conn.execute("DELETE FROM employees WHERE personnel_number=?", (pnum,))
            conn.commit()

    # ---------- ثبت روزانه ----------
    def register_employee(self, name: str, pnum: str, emp_type: str, date: str, jetty: str) -> Tuple[bool, str]:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT 1 FROM employees WHERE personnel_number=? AND date=? AND jetty_type=?",
                (pnum, date, jetty)
            )
            if c.fetchone():
                return False, "این کارمند با این تاریخ و اسکله قبلاً ثبت شده است"
            c.execute(
                "INSERT INTO employees (full_name, personnel_number, employment_type, date, jetty_type) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, pnum, emp_type, date, jetty)
            )
            conn.commit()
        return True, "ثبت با موفقیت انجام شد"

    def get_employees_by_month(self, year: str, month: str) -> List[Tuple]:
        pattern = f"{year}/{int(month):02d}/%"
        with self._connect() as conn:
            return conn.execute(
                "SELECT id, full_name, personnel_number, employment_type, date, jetty_type "
                "FROM employees WHERE date LIKE ? ORDER BY date DESC",
                (pattern,)
            ).fetchall()

    def get_employees_by_range(self, start: str, end: str) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT id, full_name, personnel_number, employment_type, date, jetty_type "
                "FROM employees WHERE date BETWEEN ? AND ? ORDER BY date DESC",
                (start, end)
            ).fetchall()

    def update_employee(self, emp_id: int, name: str, pnum: str, date: str, jetty: str) -> Tuple[bool, str]:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM employees WHERE id=?", (emp_id,))
            if not c.fetchone():
                return False, "رکورد یافت نشد"
            c.execute(
                "SELECT 1 FROM employees WHERE personnel_number=? AND date=? AND jetty_type=? AND id != ?",
                (pnum, date, jetty, emp_id)
            )
            if c.fetchone():
                return False, "این ترکیب تاریخ و اسکله قبلاً ثبت شده"
            c.execute(
                "UPDATE employees SET full_name=?, personnel_number=?, date=?, jetty_type=? WHERE id=?",
                (name, pnum, date, jetty, emp_id)
            )
            conn.commit()
        return True, "ویرایش با موفقیت انجام شد"


    def delete_employee(self, emp_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM employees WHERE id=?", (emp_id,))
            conn.commit()

    def search_employee(self, pnum: str, start: str = None, end: str = None) -> List[Tuple]:
        query = """
            SELECT full_name, personnel_number, date, jetty_type, employment_type
            FROM employees WHERE personnel_number=?
        """
        params = [pnum]
        if start and end:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start, end])
        query += " ORDER BY date"
        with self._connect() as conn:
            return conn.execute(query, params).fetchall()

    def count_days(self, pnum: str, start: str, end: str) -> Tuple[int, int]:
        rows = self.search_employee(pnum, start, end)
        east = sum(1 for r in rows if r[3] == "اسکله شرقی")
        west = sum(1 for r in rows if r[3] == "اسکله غربی")
        return east, west

    # ---------- شرح کار ----------
    def add_task(self, description: str, jetty: str, date: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO task_descriptions (description, jetty_type, date) VALUES (?, ?, ?)",
                (description, jetty, date)
            )
            conn.commit()

    def get_tasks(self) -> List[Tuple]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT id, description, jetty_type, date FROM task_descriptions ORDER BY id DESC"
            ).fetchall()

    def update_task(self, task_id: int, description: str, jetty: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE task_descriptions SET description=?, jetty_type=? WHERE id=?",
                (description, jetty, task_id)
            )
            conn.commit()

    def delete_task(self, task_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM task_descriptions WHERE id=?", (task_id,))
            conn.commit()
