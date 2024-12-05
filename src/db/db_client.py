"""
This module provides a singleton class `DbClient` to manage database connections and operations.

The `DbClient` class offers methods for performing CRUD operations and transaction management
in a PostgreSQL database using the `psycopg2` library.

Classes:
    DbClient: A singleton class to manage database connections and operations.

Usage example:
    db_config = {
        'dbname': 'your_db',
        'user': 'your_user',
        'password': 'your_password',
        'host': 'your_host',
        'port': 'your_port'
    }
    db_client = DbClient(db_config)
    db_client.insert('your_table', {'column1': 'value1', 'column2': 'value2'})
    results = db_client.fetch('your_table', {'column1': 'value1'})
"""

import psycopg2
from psycopg2 import sql
import psycopg2.extras


class DbClient:
    """
    Singleton class to manage database connections and operations.

    This class provides methods for performing CRUD operations and
    transaction management in a PostgreSQL database.
    """

    _instance = None
    _connection = None
    _cursor = None

    def __new__(cls, db_config=None):
        if cls._instance is None:
            if db_config is None:
                raise ValueError(
                    "Database configuration must be provided on first instantiation."
                )
            cls._instance = super().__new__(cls)
            cls._instance._initialize_connection(db_config)
        return cls._instance

    def _initialize_connection(self, db_config):
        """
        Initialize the database connection and cursor.

        Args:
            db_config (dict): A dictionary containing database connection details
                              (e.g., dbname, user, password, host, port).
        """
        self._connection = psycopg2.connect(**db_config)
        self._cursor = self._connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

    def insert(self, table, data) -> int:
        """
        Insert a record into the specified table.

        Args:
            table (str): Table name.
            data (dict): Dictionary of column-value pairs to insert.
        """
        columns = data.keys()
        values = data.values()
        query = sql.SQL(
            "INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING ID"
        ).format(
            table=sql.Identifier(table),
            columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
        )

        self._execute(query, tuple(values))
        response = self._cursor.fetchone()

        return response[0] if response else None

    def update(self, table, data, condition):
        """
        Update records in the specified table based on a condition.

        Args:
            table (str): Table name.
            data (dict): Dictionary of column-value pairs to update.
            condition (dict): Dictionary of column-value pairs for the WHERE clause.
        """
        set_clause = self._build_query_clause(data)
        where_clause = self._build_query_clause(condition)
        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {where_clause}").format(
            table=sql.Identifier(table),
            set_clause=sql.SQL(", ").join(set_clause),
            where_clause=sql.SQL(" AND ").join(where_clause),
        )
        params = {**data, **condition}
        return self._execute(query, params)

    def delete(self, table, condition):
        """
        Delete records from the specified table based on a condition.

        Args:
            table (str): Table name.
            condition (dict): Dictionary of column-value pairs for the WHERE clause.
        """
        where_clause = self._build_query_clause(condition)
        query = sql.SQL("DELETE FROM {table} WHERE {where_clause}").format(
            table=sql.Identifier(table),
            where_clause=sql.SQL(" AND ").join(where_clause),
        )
        return self._execute(query, condition)

    def fetch(self, table, condition=None):
        """
        Builds the SQL Query to select the records and returns the result

        Args:
            table (str): Table name.
            condition (dict, optional): Dictionary of column-value pairs for the WHERE
                                        clause. Defaults to None.

        Returns:
            list: Query results as a list of tuples.
        """
        try:
            return self.query(
                self._build_select_query(table, condition, is_count=False),
                condition,
            )
        except psycopg2.Error as e:
            self._connection.rollback()
            raise e

    def fetch_one(self, table, condition=None):
        """
        Builds the SQL Query to select one record and return the first result.

        Args:
            table (str): Table name.
            condition (dict, optional): Dictionary of column-value pairs for the WHERE
                                        clause. Defaults to None.

        Returns:
            int: Number of records in the table.
        """
        try:
            result = self.query(
                self._build_select_query(table, condition, is_count=False, limit=1),
                condition,
            )

            return result[0] if result and result[0] else None
        except psycopg2.Error as e:
            self._connection.rollback()
            raise e

    def query(self, query, params=None):
        """
        Execute a custom SQL query and return the results.

        Args:
            query (str): SQL query string with placeholders.
            params (tuple, optional): Parameters for the query placeholders. Defaults to None.

        Returns:
            list: Query results as a list of tuples.
        """
        try:
            self._cursor.execute(query, params)
            results = self._cursor.fetchall()
            return [dict(row) for row in results]
        except psycopg2.Error as e:
            self._connection.rollback()
            raise e

    def count(self, table, condition=None):
        """
        Count the number of records in the specified table.

        Args:
            table (str): Table name.
            condition (dict, optional): Dictionary of column-value pairs for the WHERE
                                        clause. Defaults to None.

        Returns:
            int: Number of records in the table.
        """
        try:
            result = self.query(
                self._build_select_query(table, condition, is_count=True),
                condition,
            )

            return (
                result[0]["count"] if result and result[0] and result[0]["count"] else 0
            )
        except psycopg2.Error as e:
            self._connection.rollback()
            raise e

    def _execute(self, query, params=None):
        """
        Execute a custom SQL query without returning results.

        Args:
            query (str): SQL query string with placeholders.
            params (tuple, optional): Parameters for the query placeholders. Defaults to None.
        """
        try:
            self._cursor.execute(query, params)
        except psycopg2.Error as e:
            self._connection.rollback()
            raise e

    def commit_transaction(self):
        """
        Commit the current transaction.

        This saves all changes made during the transaction to the database.
        """
        self._connection.commit()

    def rollback_transaction(self):
        """
        Rollback the current transaction.

        This reverts all changes made during the transaction, ensuring no partial updates.
        """
        self._connection.rollback()

    def close(self):
        """
        Close the database connection and cursor.

        This method should be called when the database is no longer needed.
        """
        self._cursor.close()
        self._connection.close()
        DbClient._instance = None

    def _build_query_clause(self, condition):
        """
        Build a WHERE / SET clause for a SQL query.

        Args:
            condition (dict): Dictionary of column-value pairs for the WHERE clause.

        Returns:
            list: List of SQL clauses for the query.
        """
        return [
            sql.SQL("{} = {}").format(
                sql.Identifier(column_key), sql.Placeholder(column_key)
            )
            for column_key in condition
        ]

    def _build_select_query(
        self,
        table: str,
        condition: dict = None,
        offset: int = None,
        limit: int = None,
        is_count=False,
    ):
        """
        Build a SELECT query with optional WHERE, OFFSET, and LIMIT

        Args:
            table (str): Name of the table
            condition (dict, optional): . Defaults to None.
            offset (int, optional): Offset from which the record has to be queried.
                                    Defaults to None.
            limit (int , optional): Limit to be applied. Defaults to None.
            is_count (bool, optional): If True, the query will return the count of records.
                                        Defaults to False.
        """
        if is_count:
            query = sql.SQL("SELECT COUNT(*) as count FROM {table}").format(
                table=sql.Identifier(table)
            )
        else:
            query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table))
        if condition:
            where_clause = self._build_query_clause(condition)
            query += sql.SQL(" WHERE {where_clause}").format(
                where_clause=sql.SQL(" AND ").join(where_clause)
            )

        if offset:
            query += sql.SQL(" OFFSET {offset}").format(offset=sql.Literal(offset))

        if limit:
            query += sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(limit))

        return query

    def __del__(self):
        """
        Destructor to ensure that the database connection is closed when the object is deleted.
        """
        self.close()
