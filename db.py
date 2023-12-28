import sqlite3

STOCK_FIELDS = [
    "Date",
    "Coût",
    "Type",
    "Marque",
    "Taille",
    "Couleur",
    "Note",
]

VENTES_FIELDS = [
    "DateAchat",
    "DateVente",
    "PrixAchat",
    "PrixVente",
]


class InventoryData:
    def __init__(self):
        self.conn = sqlite3.connect("data/inventory.db")
        self.cursor = self.conn.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS stock (ID INTEGER PRIMARY KEY, {', '.join(map(lambda label: f'{label} TEXT', STOCK_FIELDS))})"
        )
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS ventes (ID INTEGER PRIMARY KEY, {', '.join(map(lambda label: f'{label} TEXT', VENTES_FIELDS))})"
        )
        self.conn.commit()

    def list_stock(self):
        self.cursor.execute("SELECT * FROM stock")
        return [
            {
                "ID": row[0],
                **{label: row[i] for i, label in enumerate(STOCK_FIELDS, start=1)},
            }
            for row in self.cursor.fetchall()
        ]

    def list_ventes(self):
        self.cursor.execute("SELECT * FROM ventes")
        return [
            {
                "ID": row[0],
                **{label: row[i] for i, label in enumerate(VENTES_FIELDS, start=1)},
            }
            for row in self.cursor.fetchall()
        ]

    def get_from_stock(self, item_id):
        self.cursor.execute("SELECT * FROM stock WHERE ID = ?", (item_id,))
        row = self.cursor.fetchone()
        return {
            "ID": row[0],
            **{label: row[i] for i, label in enumerate(STOCK_FIELDS, start=1)},
        }

    def get_from_ventes(self, item_id):
        self.cursor.execute("SELECT * FROM ventes WHERE ID = ?", (item_id,))
        row = self.cursor.fetchone()
        return {
            "ID": row[0],
            **{label: row[i] for i, label in enumerate(VENTES_FIELDS, start=1)},
        }

    def add_item_to_stock(self, item):
        self.cursor.execute(
            f"INSERT INTO stock ({', '.join(STOCK_FIELDS)}) VALUES ({', '.join('?' for _ in STOCK_FIELDS)})",
            tuple(item[label] for label in STOCK_FIELDS),
        )
        self.conn.commit()

    def delete_item_from_stock(self, item_id):
        self.cursor.execute("DELETE FROM stock WHERE ID = ?", (item_id,))
        self.conn.commit()

    def edit_item_from_stock(self, item_id, new_item):
        self.cursor.execute(
            f"UPDATE stock SET {', '.join(map(lambda label: f'{label} = ?', STOCK_FIELDS))} WHERE ID = ?",
            (
                *tuple(new_item[label] for label in STOCK_FIELDS),
                item_id,
            ),
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()
