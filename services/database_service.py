import sqlite3

from datetime import datetime


class DatabaseService:

    def __init__(self, db_path):

        self.connection = sqlite3.connect(
            db_path
        )

        self.cursor = self.connection.cursor()

    def create_table(self):

        query = """

        CREATE TABLE IF NOT EXISTS processed_tickets (

            ticket_number TEXT PRIMARY KEY,

            assigned_engineer TEXT,

            processed_time TEXT

        )

        """

        self.cursor.execute(query)

        self.connection.commit()

    def is_ticket_processed(
            self,
            ticket_number
    ):

        query = """

        SELECT ticket_number

        FROM processed_tickets

        WHERE ticket_number = ?

        """

        self.cursor.execute(
            query,
            (ticket_number,)
        )

        result = self.cursor.fetchone()

        return result is not None

    def save_processed_ticket(

            self,
            ticket_number,
            assigned_engineer

    ):

        query = """

        INSERT INTO processed_tickets (

            ticket_number,
            assigned_engineer,
            processed_time

        )

        VALUES (?, ?, ?)

        """

        self.cursor.execute(

            query,

            (
                ticket_number,
                assigned_engineer,
                str(datetime.now().isoformat())
            )

        )

        self.connection.commit()
    
