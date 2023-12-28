import random
import string
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from ttkthemes import ThemedTk

from config import FORM_LABELS
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
            columns=("ID", *FORM_LABELS),
            show="headings",
            selectmode="extended",
        )
        self.tree.heading("ID", text="ID")
        for label in FORM_LABELS:
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
        for item in self.data.load_data():
            self.tree.insert(
                "",
                "end",
                values=(
                    item["ID"],
                    *tuple(item[label] for label in FORM_LABELS),
                ),
            )
        self.autosize_columns()

    def create_form(self, frame, initial_values: dict = None):
        if initial_values is None:
            initial_values = {}

        entries = {}
        for i, label in enumerate(FORM_LABELS):
            ttk.Label(frame, text=label).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=5
            )
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
            entry.insert(0, initial_values.get(label, ""))

            entries[label] = entry
        return entries

    def test_form(self):
        def submit():
            item = {name: entries[name].get() for name in FORM_LABELS}
            self.data.add_item(item)
            self.refresh_list()
            main_window.destroy()

        main_window = tk.Toplevel(self.root)
        main_window.title("Ajouter un item")
        main_window.geometry("300x200")

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entries = self.create_form(main_frame)

        submit_button = ttk.Button(main_frame, text="Ajouter", command=submit)
        submit_button.grid(row=4, column=1)

    def add_item(self):
        def submit():
            item = {name: entries[name].get() for name in FORM_LABELS}
            self.data.add_item(item)
            self.refresh_list()
            main_window.destroy()

        def randomize_fields():
            for label in FORM_LABELS:
                entries[label].delete(0, tk.END)
                entries[label].insert(
                    0, "".join(random.choices(string.ascii_letters, k=15))
                )

        main_window = tk.Toplevel(self.root)
        main_window.title("Ajouter un item")
        main_window.geometry("300x200")

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entries = self.create_form(main_frame)

        submit_button = ttk.Button(main_frame, text="Ajouter", command=submit)
        submit_button.grid(row=4, column=1)

        randomize_button = ttk.Button(
            main_frame, text="Randomize", command=randomize_fields
        )
        randomize_button.grid(row=5, column=1)

    def edit_item(self):
        def submit():
            new_item = {name: entries[name].get() for name in FORM_LABELS}
            self.data.edit_item(item_id, new_item)
            self.refresh_list()
            main_window.destroy()

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Merci de selectionner un item à editer.")
            return

        item_id = self.tree.item(selected_item, "values")[0]
        item = self.data.load_item(item_id)

        main_window = tk.Toplevel(self.root)
        main_window.title("Modifier un item")
        main_window.geometry("300x200")

        main_frame = ttk.Frame(main_window)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entries = self.create_form(main_frame, item)

        submit_button = ttk.Button(main_frame, text="Modifier", command=submit)
        submit_button.grid(row=4, column=1)

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
    window = ThemedTk(theme="arc")
    app = InventoryApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
