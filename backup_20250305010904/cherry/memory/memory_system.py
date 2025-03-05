import sqlite3

class MemorySystem:
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT
                )
            ''')

    def set_context(self, key, value):
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO context (key, value) VALUES (?, ?)
            ''', (key, value))

    def get_context(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM context WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def clear_context(self):
        with self.conn:
            self.conn.execute('DELETE FROM context')
