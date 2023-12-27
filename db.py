import sqlite3


class InventoryData:
    def __init__(self):
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS items 
                               (id INTEGER PRIMARY KEY, nom TEXT, taille TEXT, marque TEXT, note TEXT)"""
        )
        self.conn.commit()

    def load_data(self):
        self.cursor.execute("SELECT * FROM items")
        return [
            {
                "id": row[0],
                "nom": row[1],
                "taille": row[2],
                "marque": row[3],
                "note": row[4],
            }
            for row in self.cursor.fetchall()
        ]

    def add_item(self, item):
        self.cursor.execute(
            "INSERT INTO items (nom, taille, marque, note) VALUES (?, ?, ?, ?)",
            (item["nom"], item["taille"], item["marque"], item["note"]),
        )
        self.conn.commit()

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def edit_item(self, item_id, new_item):
        self.cursor.execute(
            "UPDATE items SET nom = ?, taille = ?, marque = ?, note = ? WHERE id = ?",
            (
                new_item["nom"],
                new_item["taille"],
                new_item["marque"],
                new_item["note"],
                item_id,
            ),
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()
