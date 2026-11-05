
import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import sqlglot
from sqlglot import exp


# Database location
DB_FOLDER = Path("data")
DB_FOLDER.mkdir(exist_ok=True)

DB_PATH = DB_FOLDER / "querymind.db"


# ----------------------------------
# 1. DATABASE CONNECTION
# ----------------------------------

def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ----------------------------------
# 2. CREATE DATABASE TABLES
# ----------------------------------

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT,
            signup_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_total REAL,
            order_date TEXT,
            status TEXT,
            FOREIGN KEY(customer_id)
                REFERENCES customers(customer_id),
            FOREIGN KEY(product_id)
                REFERENCES products(product_id)
        )
    """)

    cursor.execute(
        "SELECT COUNT(*) FROM customers"
    )

    if cursor.fetchone()[0] == 0:

        random.seed(42)

        first_names = [
            "Rahul", "Ganesh", "Arjun", "Kiran",
            "David", "John", "Ravi", "Suresh",
            "Priya", "Anjali", "Sneha", "Divya"
        ]

        last_names = [
            "Reddy", "Kumar", "Sharma", "Patel",
            "Verma", "Rao", "Singh", "Das"
        ]

        cities = [
            "Hyderabad", "Bangalore", "Chennai",
            "Mumbai", "Delhi", "Pune"
        ]

        customers = []

        for i in range(1, 61):

            name = (
                random.choice(first_names) + " " +
                random.choice(last_names)
            )

            email = f"customer{i}@example.com"

            city = random.choice(cities)

            signup_date = (
                date.today() -
                timedelta(days=random.randint(30, 900))
            ).isoformat()

            customers.append(
                (i, name, email, city, signup_date)
            )

        cursor.executemany("""
            INSERT INTO customers
            VALUES (?, ?, ?, ?, ?)
        """, customers)

        categories = [
            "Electronics", "Clothing", "Books",
            "Home", "Sports", "Accessories"
        ]

        products = []

        for i in range(1, 61):

            category = random.choice(categories)

            name = f"{category} Product {i}"

            price = round(
                random.uniform(100, 50000), 2
            )

            stock = random.randint(0, 100)

            products.append(
                (i, name, category, price, stock)
            )

        cursor.executemany("""
            INSERT INTO products
            VALUES (?, ?, ?, ?, ?)
        """, products)

        orders = []

        statuses = [
            "Delivered", "Pending",
            "Shipped", "Cancelled"
        ]

        for i in range(1, 151):

            customer_id = random.randint(1, 60)

            product_id = random.randint(1, 60)

            quantity = random.randint(1, 5)

            product_price = products[product_id - 1][3]

            order_total = round(
                product_price * quantity, 2
            )

            order_date = (
                date.today() -
                timedelta(days=random.randint(0, 365))
            ).isoformat()

            status = random.choice(statuses)

            orders.append((
                i, customer_id, product_id,
                quantity, order_total,
                order_date, status
            ))

        cursor.executemany("""
            INSERT INTO orders
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, orders)

    conn.commit()
    conn.close()


# ----------------------------------
# 3. GET DATABASE SCHEMA
# ----------------------------------

def get_database_schema():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
    """)

    tables = cursor.fetchall()

    schema = ""

    for table in tables:

        table_name = table[0]

        cursor.execute(
            f"PRAGMA table_info('{table_name}')"
        )

        columns = cursor.fetchall()

        schema += f"\nTABLE: {table_name}\n"

        for column in columns:

            column_name = column[1]
            data_type = column[2]
            primary_key = column[5]

            schema += (
                f"- {column_name} ({data_type})"
            )

            if primary_key:
                schema += " PRIMARY KEY"

            schema += "\n"

        cursor.execute(
            f"PRAGMA foreign_key_list('{table_name}')"
        )

        foreign_keys = cursor.fetchall()

        for fk in foreign_keys:

            schema += (
                f"FOREIGN KEY: {table_name}.{fk[3]} "
                f"REFERENCES {fk[2]}.{fk[4]}\n"
            )

    conn.close()

    return schema


# ----------------------------------
# 4. VALIDATE SQL QUERY
# ----------------------------------

def validate_sql(sql):

    if not sql or not sql.strip():

        raise ValueError(
            "SQL query cannot be empty."
        )

    try:

        # Parse the SQL statement
        statements = sqlglot.parse(
            sql,
            read="sqlite"
        )

        # Allow exactly one SQL statement
        if len(statements) != 1 or statements[0] is None:

            raise ValueError(
                "Only one SQL statement is allowed."
            )

        tree = statements[0]

        # Allow SELECT, UNION, INTERSECT and EXCEPT
        allowed_types = (
            exp.Select,
            exp.Union,
            exp.Intersect,
            exp.Except
        )

        if not isinstance(tree, allowed_types):

            raise ValueError(
                "Only SELECT queries are permitted."
            )

        return True

    except sqlglot.errors.ParseError as e:

        raise ValueError(
            f"Invalid SQL syntax: {e}"
        ) from e


# ----------------------------------
# 5. READ-ONLY DATABASE EXECUTION
# ----------------------------------

def execute_read_query(sql):

    # Validate SQL before execution
    validate_sql(sql)

    conn = get_connection()

    try:

        # Enable SQLite read-only query mode
        conn.execute("PRAGMA query_only = ON")

        # Allow only database-reading operations
        allowed_actions = {
            sqlite3.SQLITE_SELECT,
            sqlite3.SQLITE_READ,
            sqlite3.SQLITE_FUNCTION,
            sqlite3.SQLITE_RECURSIVE
        }

        def authorizer(
            action, arg1, arg2, database, trigger
        ):

            if action in allowed_actions:
                return sqlite3.SQLITE_OK

            return sqlite3.SQLITE_DENY

        conn.set_authorizer(authorizer)

        # Limit expensive queries to approximately
        # 3 million SQLite virtual machine instructions
        instruction_count = 0

        def query_limit():

            nonlocal instruction_count

            instruction_count += 1000

            return instruction_count > 3_000_000

        conn.set_progress_handler(query_limit, 1000)

        # Execute the SQL query
        cursor = conn.cursor()

        cursor.execute(sql)

        # Get column names dynamically
        columns = [
            description[0]
            for description in cursor.description
        ]

        # Get query results
        rows = cursor.fetchall()

        # Convert results into DataFrame
        df = pd.DataFrame(
            rows,
            columns=columns
        )

        return df

    except sqlite3.DatabaseError as e:

        message = str(e)

        if "no such table" in message:
            raise ValueError(
                "The requested table does not exist."
            ) from e

        elif "no such column" in message:
            raise ValueError(
                "The requested column does not exist."
            ) from e

        elif "interrupted" in message:
            raise ValueError(
                "Query stopped because it exceeded "
                "the execution limit."
            ) from e

        elif "not authorized" in message:
            raise ValueError(
                "This query contains a prohibited "
                "database operation."
            ) from e

        else:
            raise ValueError(
                f"Database error: {message}"
            ) from e

    finally:

        conn.close()


# ----------------------------------
# 6. GET TABLE COUNTS
# ----------------------------------

def get_table_counts():

    conn = get_connection()

    cursor = conn.cursor()

    tables = [
        "customers",
        "products",
        "orders"
    ]

    counts = {}

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        counts[table] = cursor.fetchone()[0]

    conn.close()

    return counts
