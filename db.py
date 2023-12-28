import sqlite3

from config import FORM_LABELS


class InventoryData:
    def __init__(self):
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS items (ID INTEGER PRIMARY KEY, {', '.join(map(lambda label: f'{label} TEXT', FORM_LABELS))})"
        )
        self.conn.commit()

    def load_data(self):
        self.cursor.execute("SELECT * FROM items")
        return [
            {
                "ID": row[0],
                **{label: row[i] for i, label in enumerate(FORM_LABELS, start=1)},
            }
            for row in self.cursor.fetchall()
        ]

    def load_item(self, item_id):
        self.cursor.execute("SELECT * FROM items WHERE ID = ?", (item_id,))
        row = self.cursor.fetchone()
        return {
            "ID": row[0],
            **{label: row[i] for i, label in enumerate(FORM_LABELS, start=1)},
        }

    def add_item(self, item):
        self.cursor.execute(
            f"INSERT INTO items ({', '.join(FORM_LABELS)}) VALUES (?, ?, ?, ?)",
            tuple(item[label] for label in FORM_LABELS),
        )
        self.conn.commit()

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM items WHERE ID = ?", (item_id,))
        self.conn.commit()

    def edit_item(self, item_id, new_item):
        self.cursor.execute(
            f"UPDATE items SET {', '.join(map(lambda label: f'{label} = ?', FORM_LABELS))} WHERE ID = ?",
            (
                *tuple(new_item[label] for label in FORM_LABELS),
                item_id,
            ),
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()
