import random
import string
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import messagebox, ttk

from ttkthemes import ThemedTk

from autocomplete import STOCK_FIELD_PROPOSITIONS
from customWidgets import AutocompleteCombobox, AutocompleteEntry
from db import STOCK_FIELDS, InventoryData

MAIN_GEOMETRY = "1000x800"
FORM_GEOMETRY = "400x300"


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventaire")
        self.root.geometry(MAIN_GEOMETRY)
        self.data = InventoryData()

        # Create a notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Stock")
        self.sold_items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sold_items_frame, text="Ventes")

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

        self.edit_button = ttk.Button(
            button_frame, text="Modifier", command=self.edit_item
        )
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = ttk.Button(
            button_frame, text="Supprimer", command=self.delete_item
        )
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("ID", *STOCK_FIELDS),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("ID", text="ID")
        for label in STOCK_FIELDS:
            self.tree.heading(label, text=label)

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
        for item in self.data.list_stock():
            self.tree.insert(
                "",
                "end",
                values=(
                    item["ID"],
                    *tuple(item[label] for label in STOCK_FIELDS),
                ),
            )
        self.autosize_columns()

    def create_form(self, frame, initial_values: dict = None):
        if initial_values is None:
            initial_values = {}

        entries = {}
        for i, label in enumerate(STOCK_FIELDS):
            l = ttk.Label(frame, text=f"{label}:")
            l.grid(row=i, column=0, sticky=tk.W, padx=[15, 5], pady=5)
            if label in STOCK_FIELD_PROPOSITIONS:
                entry = AutocompleteCombobox(frame)
                entry.set_completion_list(STOCK_FIELD_PROPOSITIONS[label])
            else:
                entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=[0, 5], pady=5)
            entry.insert(0, initial_values.get(label, ""))

            entries[label] = entry
        return entries

    def add_item(self):
        def submit():
            item = {name: entries[name].get() for name in STOCK_FIELDS}
            self.data.add_item_to_stock(item)
            self.refresh_list()
            main_window.destroy()

        def randomize_fields():
            for label in STOCK_FIELDS:
                entries[label].delete(0, tk.END)
                entries[label].insert(
                    0, "".join(random.choices(string.ascii_letters, k=15))
                )

        main_window = tk.Toplevel(self.root)
        main_window.title("Ajouter un item")
        main_window.geometry(FORM_GEOMETRY)

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entries = self.create_form(main_frame)
        entries["Date"].delete(0, tk.END)
        entries["Date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        # randomize_fields()

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(len(FORM_GEOMETRY), weight=1)

        submit_button = ttk.Button(main_frame, text="Ajouter", command=submit)
        submit_button.grid(row=len(STOCK_FIELDS), column=1, padx=50, pady=5, sticky=tk.EW)

    def edit_item(self):
        def submit():
            new_item = {name: entries[name].get() for name in STOCK_FIELDS}
            self.data.edit_item_from_stock(item_id, new_item)
            self.refresh_list()
            main_window.destroy()

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Merci de selectionner un item à editer.")
            return

        item_id = self.tree.item(selected_item, "values")[0]
        item = self.data.get_from_stock(item_id)

        main_window = tk.Toplevel(self.root)
        main_window.title("Modifier un item")
        main_window.geometry(FORM_GEOMETRY)

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entries = self.create_form(main_frame, item)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(len(FORM_GEOMETRY), weight=1)

        submit_button = ttk.Button(main_frame, text="Modifier", command=submit)
        submit_button.grid(row=len(STOCK_FIELDS), column=1, padx=50, pady=5, sticky=tk.EW)

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
                self.data.delete_item_from_stock(item_id)
            self.refresh_list()

    def sell_item(self):
        self.test_form()

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


def main():
    window = ThemedTk(theme="Adapta")
    app = InventoryApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
