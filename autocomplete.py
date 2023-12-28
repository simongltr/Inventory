import unicodedata

from db import STOCK_FIELDS

STOCK_FIELD_PROPOSITIONS = {}
for label in STOCK_FIELDS:
    normalized = (
        unicodedata.normalize("NFKD", label).encode("ASCII", "ignore").decode().lower()
    )
    filepath = f"data/{normalized}.txt"
    try:
        with open(filepath, "r") as f:
            STOCK_FIELD_PROPOSITIONS[label] = sorted(
                [line.strip() for line in f.readlines()]
            )
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    print(STOCK_FIELD_PROPOSITIONS)
