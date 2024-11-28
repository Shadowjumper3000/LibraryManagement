import tkinter as tk
from tkinter import messagebox
import sqlite3
import json
import os


def setup_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    isbn TEXT UNIQUE,
    notes TEXT,
    current_page INTEGER
    )
    """
    )
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN current_page INTEGER")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    conn.commit()
    conn.close()


def add_book():
    if validate_fields():
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, year, isbn, notes, current_page) VALUES (?, ?, ?, ?, ?, ?)",
            (
                title_entry.get(),
                author_entry.get(),
                year_entry.get(),
                isbn_entry.get(),
                notes_entry.get(),
                current_page_entry.get(),
            ),
        )
        conn.commit()
        conn.close()
        clear_fields()
        fetch_all_books()
    else:
        messagebox.showerror("Input Error", "All fields must be filled out")


def search_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if title_entry.get() and title_entry.get() != "Enter Title":
        query += " AND title LIKE ?"
        params.append("%" + title_entry.get() + "%")
    if author_entry.get() and author_entry.get() != "Enter Author":
        query += " AND author LIKE ?"
        params.append("%" + author_entry.get() + "%")
    if year_entry.get() and year_entry.get() != "Enter Year":
        query += " AND year LIKE ?"
        params.append("%" + year_entry.get() + "%")
    if isbn_entry.get() and isbn_entry.get() != "Enter ISBN":
        query += " AND isbn LIKE ?"
        params.append("%" + isbn_entry.get() + "%")
    if notes_entry.get() and notes_entry.get() != "Enter Notes":
        query += " AND notes LIKE ?"
        params.append("%" + notes_entry.get() + "%")
    if current_page_entry.get() and current_page_entry.get() != "Enter Current Page":
        query += " AND current_page LIKE ?"
        params.append("%" + current_page_entry.get() + "%")

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    update_listbox(results)


def fetch_all_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    results = cursor.fetchall()
    conn.close()
    update_listbox(results)


def delete_book():
    selected_book = listbox.curselection()
    if selected_book:
        book_id = listbox.get(selected_book)[0]
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        fetch_all_books()
    else:
        messagebox.showerror("Selection Error", "No book selected")


def update_book():
    selected_book = listbox.curselection()
    if selected_book and validate_fields():
        book_id = listbox.get(selected_book)[0]
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET title = ?, author = ?, year = ?, isbn = ?, notes = ?, current_page = ? WHERE id = ?",
            (
                title_entry.get(),
                author_entry.get(),
                year_entry.get(),
                isbn_entry.get(),
                notes_entry.get(),
                current_page_entry.get(),
                book_id,
            ),
        )
        conn.commit()
        conn.close()
        clear_fields()
        fetch_all_books()
    else:
        messagebox.showerror("Selection/Error", "No book selected or fields are empty")


def clear_fields():
    title_entry.delete(0, tk.END)
    title_entry.insert(0, "Enter Title")
    author_entry.delete(0, tk.END)
    author_entry.insert(0, "Enter Author")
    year_entry.delete(0, tk.END)
    year_entry.insert(0, "Enter Year")
    isbn_entry.delete(0, tk.END)
    isbn_entry.insert(0, "Enter ISBN")
    notes_entry.delete(0, tk.END)
    notes_entry.insert(0, "Enter Notes")
    current_page_entry.delete(0, tk.END)
    current_page_entry.insert(0, "Enter Current Page")


def update_listbox(results):
    listbox.delete(0, tk.END)
    for row in results:
        display_text = (
            f"{row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}"
        )
        listbox.insert(tk.END, display_text)


def validate_fields():
    return all(
        [
            title_entry.get() and title_entry.get() != "Enter Title",
            author_entry.get() and author_entry.get() != "Enter Author",
            year_entry.get() and year_entry.get() != "Enter Year",
            isbn_entry.get() and isbn_entry.get() != "Enter ISBN",
            notes_entry.get() and notes_entry.get() != "Enter Notes",
            current_page_entry.get()
            and current_page_entry.get() != "Enter Current Page",
        ]
    )


def load_preferences():
    if os.path.exists("preferences.json"):
        with open("preferences.json", "r") as file:
            preferences = json.load(file)
            root.geometry(preferences.get("window_geometry", ""))
            root.update_idletasks()


def save_preferences():
    preferences = {"window_geometry": root.geometry()}
    with open("preferences.json", "w") as file:
        json.dump(preferences, file)


def on_entry_click(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, tk.END)
        entry.insert(0, "")
        entry.config(fg="black")


def on_focusout(event, entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)
        entry.config(fg="grey")


# Setup the database
setup_database()

# Create the main application window
root = tk.Tk()
root.title("Library Management System")
root.protocol("WM_DELETE_WINDOW", lambda: [save_preferences(), root.destroy()])

# Load user preferences
load_preferences()

# Create input fields with default text
title_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
title_entry.grid(row=0, column=0, padx=10, pady=5)
title_entry.insert(0, "Enter Title")
title_entry.bind(
    "<FocusIn>", lambda event: on_entry_click(event, title_entry, "Enter Title")
)
title_entry.bind(
    "<FocusOut>", lambda event: on_focusout(event, title_entry, "Enter Title")
)

author_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
author_entry.grid(row=1, column=0, padx=10, pady=5)
author_entry.insert(0, "Enter Author")
author_entry.bind(
    "<FocusIn>", lambda event: on_entry_click(event, author_entry, "Enter Author")
)
author_entry.bind(
    "<FocusOut>", lambda event: on_focusout(event, author_entry, "Enter Author")
)

year_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
year_entry.grid(row=2, column=0, padx=10, pady=5)
year_entry.insert(0, "Enter Year")
year_entry.bind(
    "<FocusIn>", lambda event: on_entry_click(event, year_entry, "Enter Year")
)
year_entry.bind(
    "<FocusOut>", lambda event: on_focusout(event, year_entry, "Enter Year")
)

isbn_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
isbn_entry.grid(row=3, column=0, padx=10, pady=5)
isbn_entry.insert(0, "Enter ISBN")
isbn_entry.bind(
    "<FocusIn>", lambda event: on_entry_click(event, isbn_entry, "Enter ISBN")
)
isbn_entry.bind(
    "<FocusOut>", lambda event: on_focusout(event, isbn_entry, "Enter ISBN")
)

notes_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
notes_entry.grid(row=4, column=0, padx=10, pady=5)
notes_entry.insert(0, "Enter Notes")
notes_entry.bind(
    "<FocusIn>", lambda event: on_entry_click(event, notes_entry, "Enter Notes")
)
notes_entry.bind(
    "<FocusOut>", lambda event: on_focusout(event, notes_entry, "Enter Notes")
)

current_page_entry = tk.Entry(root, font=("Arial", 12), fg="grey")
current_page_entry.grid(row=5, column=0, padx=10, pady=5)
current_page_entry.insert(0, "Enter Current Page")
current_page_entry.bind(
    "<FocusIn>",
    lambda event: on_entry_click(event, current_page_entry, "Enter Current Page"),
)
current_page_entry.bind(
    "<FocusOut>",
    lambda event: on_focusout(event, current_page_entry, "Enter Current Page"),
)

# Create buttons and move them to the right of the input boxes
add_button = tk.Button(
    root, text="Add Book", command=add_book, font=("Arial", 12), bg="lightgreen"
)
add_button.grid(row=0, column=1, padx=10, pady=5)

search_button = tk.Button(
    root, text="Search Book", command=search_books, font=("Arial", 12), bg="lightgreen"
)
search_button.grid(row=1, column=1, padx=10, pady=5)

show_all_button = tk.Button(
    root,
    text="Show All Books",
    command=fetch_all_books,
    font=("Arial", 12),
    bg="lightgreen",
)
show_all_button.grid(row=2, column=1, padx=10, pady=5)

delete_button = tk.Button(
    root, text="Delete Book", command=delete_book, font=("Arial", 12), bg="lightgreen"
)
delete_button.grid(row=3, column=1, padx=10, pady=5)

update_button = tk.Button(
    root, text="Update Book", command=update_book, font=("Arial", 12), bg="lightgreen"
)
update_button.grid(row=4, column=1, padx=10, pady=5)

clear_button = tk.Button(
    root, text="Clear Fields", command=clear_fields, font=("Arial", 12), bg="lightgreen"
)
clear_button.grid(row=5, column=1, padx=10, pady=5)

# Create Quit button
quit_button = tk.Button(
    root, text="Quit", command=root.quit, font=("Arial", 12), bg="lightcoral"
)
quit_button.grid(row=6, column=1, padx=10, pady=5)

# Create Listbox and Scrollbar
listbox = tk.Listbox(root, height=10, width=50, font=("Arial", 12))
listbox.grid(row=7, column=0, columnspan=2, rowspan=6, sticky="nsew", padx=10, pady=5)

scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=7, column=2, rowspan=6, sticky="ns")

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Configure grid to expand with window
root.grid_rowconfigure(7, weight=1)
root.grid_columnconfigure(0, weight=1)

# Run the application
root.mainloop()
