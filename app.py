import random
import string
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from ttkthemes import ThemedTk

from db import InventoryData


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventaire")
        self.root.geometry("1000x800")
        self.data = InventoryData()

        # Create a notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Stock")
        self.sold_items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sold_items_frame, text="Vendus")

        self.notebook.bind("<<NotebookTabChanged>>", lambda _: self.on_tab_selected())

        # Create widgets for each tab
        self.create_inventory_widgets(self.inventory_frame)
        self.create_sold_items_widgets(self.sold_items_frame)

        self.refresh_list()
        self.uptade_button_state()

    def create_inventory_widgets(self, frame: ttk.Frame):
        self.root.bind("<Escape>", lambda _: self.on_escape_key())

        main_frame = ttk.Frame(frame)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(frame)
        button_frame.grid(in_=main_frame, row=3, column=0, sticky=tk.NSEW)

        self.add_button = ttk.Button(button_frame, text="Ajouter", command=self.add_item)
        self.add_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.sell_button = ttk.Button(button_frame, text="Vendre", command=self.sell_item)
        self.sell_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.edit_button = ttk.Button(button_frame, text="Editer", command=self.edit_item)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = ttk.Button(
            button_frame, text="Supprimer", command=self.delete_item
        )
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("id", "nom", "taille", "marque", "note"),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("taille", text="Taille")
        self.tree.heading("marque", text="Marque")
        self.tree.heading("note", text="Note")

        self.y_scrollbar = ttk.Scrollbar(orient=tk.VERTICAL, command=self.tree.yview)
        self.x_scrollbar = ttk.Scrollbar(orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree["yscroll"] = self.y_scrollbar.set
        self.tree["xscroll"] = self.x_scrollbar.set
        self.tree.bind("<Button-1>", lambda e: self.on_treeview_click(e.y))
        self.tree.bind("<<TreeviewSelect>>", lambda _: self.uptade_button_state())

        self.tree.grid(in_=main_frame, row=0, column=0, sticky=tk.NSEW)
        self.y_scrollbar.grid(in_=main_frame, row=0, column=1, sticky=tk.NS)
        self.x_scrollbar.grid(in_=main_frame, row=1, column=0, sticky=tk.EW)

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def create_sold_items_widgets(self, frame):
        pass

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.data.load_data():
            self.tree.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["nom"],
                    item["taille"],
                    item["marque"],
                    item["note"],
                ),
            )
        self.autosize_columns()

    def add_item(self):
        def submit():
            item = {
                "nom": entry_name.get(),
                "taille": entry_size.get(),
                "marque": entry_brand.get(),
                "note": entry_note.get(),
            }
            self.data.add_item(item)
            self.refresh_list()
            main_window.destroy()

        def randomize_fields():
            entry_name.delete(0, tk.END)
            entry_name.insert(
                0, "".join(random.choices(string.ascii_letters + string.digits, k=10))
            )
            entry_size.delete(0, tk.END)
            entry_size.insert(0, "".join(random.choices(string.digits, k=2)))
            entry_brand.delete(0, tk.END)
            entry_brand.insert(0, "".join(random.choices(string.ascii_letters, k=5)))
            entry_note.delete(0, tk.END)
            entry_note.insert(
                0, "".join(random.choices(string.ascii_letters + string.digits, k=15))
            )

        main_window = tk.Toplevel(self.root)
        main_window.title("Ajouter un item")
        main_window.geometry("300x200")

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Nom:").grid(row=0, column=0)
        entry_name = ttk.Entry(main_frame)
        entry_name.grid(row=0, column=1)

        ttk.Label(main_frame, text="Taille:").grid(row=1, column=0)
        entry_size = ttk.Entry(main_frame)
        entry_size.grid(row=1, column=1)

        ttk.Label(main_frame, text="Marque:").grid(row=2, column=0)
        entry_brand = ttk.Entry(main_frame)
        entry_brand.grid(row=2, column=1)

        ttk.Label(main_frame, text="Note:").grid(row=3, column=0)
        entry_note = ttk.Entry(main_frame)
        entry_note.grid(row=3, column=1)

        submit_button = ttk.Button(main_frame, text="Ajouter", command=submit)
        submit_button.grid(row=4, column=1)

        randomize_button = ttk.Button(
            main_frame, text="Randomize", command=randomize_fields
        )
        randomize_button.grid(row=5, column=1)

    def delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "Warning", "Please select one or more items to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete the selected items?"
        ):
            for item in selected_items:
                item_id = self.tree.item(item, "values")[0]
                self.data.delete_item(item_id)
            self.refresh_list()

    def edit_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Merci de selectionner un item à editer.")
            return

        def submit():
            updated_item = {
                "nom": entry_name.get(),
                "taille": entry_size.get(),
                "marque": entry_brand.get(),
                "note": entry_note.get(),
            }
            self.data.edit_item(item_id, updated_item)
            self.refresh_list()
            main_window.destroy()

        item_id = self.tree.item(selected_item, "values")[0]
        item = self.data.load_data()[int(item_id) - 1]

        main_window = tk.Toplevel(self.root)
        main_window.title("Ajouter un item")
        main_window.geometry("300x200")

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Nom:").grid(row=0, column=0)
        entry_name = ttk.Entry(main_frame)
        entry_name.insert(0, item["nom"])
        entry_name.grid(row=0, column=1)

        ttk.Label(main_frame, text="Taille:").grid(row=1, column=0)
        entry_size = ttk.Entry(main_frame)
        entry_size.insert(0, item["taille"])
        entry_size.grid(row=1, column=1)

        ttk.Label(main_frame, text="Marque:").grid(row=2, column=0)
        entry_brand = ttk.Entry(main_frame)
        entry_brand.insert(0, item["marque"])
        entry_brand.grid(row=2, column=1)

        ttk.Label(main_frame, text="Note:").grid(row=3, column=0)
        entry_note = ttk.Entry(main_frame)
        entry_note.insert(0, item["note"])
        entry_note.grid(row=3, column=1)

        submit_button = ttk.Button(main_frame, text="Editer", command=submit)
        submit_button.grid(row=4, column=1)

    def sell_item(self):
        ...

    def autosize_columns(self):
        for i in range(len(self.tree["columns"]))[:-1]:
            w = tkfont.Font().measure(self.tree.heading(i, "text"))
            for item in self.tree.get_children():
                w = max(w, tkfont.Font().measure(self.tree.set(item, i)))
            self.tree.column(self.tree["columns"][i], stretch=tk.NO, width=w + 30)

    # Event handlers

    def on_treeview_click(self, y):
        if self.tree.identify_row(y) == "":
            self.tree.selection_remove(self.tree.selection())

    def on_escape_key(self):
        self.tree.selection_remove(self.tree.selection())

    def on_tab_selected(self):
        # Ensures the tab is fully drawn at click time
        self.notebook.update_idletasks()

    def autocomplete(self, txt, lst):
        if not txt:
            return lst
        return [x for x in lst if x.startswith(txt)]

    def uptade_button_state(self):
        selected_items = self.tree.selection()

        if len(selected_items) != 1:
            self.edit_button.config(state=tk.DISABLED)
            self.sell_button.config(state=tk.DISABLED)
        else:
            self.edit_button.config(state=tk.NORMAL)
            self.sell_button.config(state=tk.NORMAL)

        if len(selected_items) == 0:
            self.delete_button.config(state=tk.DISABLED)
        else:
            self.delete_button.config(state=tk.NORMAL)

    def on_tab_selected(self, event):
        # Ensures the tab is fully drawn at click time
        self.notebook.update_idletasks()


def main():
    window = ThemedTk(theme="arc")
    app = InventoryApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
