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
    isbn TEXT UNIQUE
    )
    """
    )
    conn.commit()
    conn.close()


def add_book():
    if validate_fields():
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
            (title_entry.get(), author_entry.get(), year_entry.get(), isbn_entry.get()),
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
    cursor.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ? OR isbn LIKE ?",
        (
            "%" + title_entry.get() + "%",
            "%" + author_entry.get() + "%",
            "%" + year_entry.get() + "%",
            "%" + isbn_entry.get() + "%",
        ),
    )
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
            "UPDATE books SET title = ?, author = ?, year = ?, isbn = ? WHERE id = ?",
            (
                title_entry.get(),
                author_entry.get(),
                year_entry.get(),
                isbn_entry.get(),
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
    author_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)
    isbn_entry.delete(0, tk.END)


def update_listbox(results):
    listbox.delete(0, tk.END)
    for row in results:
        listbox.insert(tk.END, row)


def validate_fields():
    return all(
        [title_entry.get(), author_entry.get(), year_entry.get(), isbn_entry.get()]
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


# Setup the database
setup_database()

# Create the main application window
root = tk.Tk()
root.title("Library Management System")
root.protocol("WM_DELETE_WINDOW", lambda: [save_preferences(), root.destroy()])

# Load user preferences
load_preferences()

# Create input fields
tk.Label(root, text="Title").grid(row=0, column=0)
title_entry = tk.Entry(root)
title_entry.grid(row=0, column=1)

tk.Label(root, text="Author").grid(row=1, column=0)
author_entry = tk.Entry(root)
author_entry.grid(row=1, column=1)

tk.Label(root, text="Year").grid(row=2, column=0)
year_entry = tk.Entry(root)
year_entry.grid(row=2, column=1)

tk.Label(root, text="ISBN").grid(row=3, column=0)
isbn_entry = tk.Entry(root)
isbn_entry.grid(row=3, column=1)

# Create buttons
add_button = tk.Button(root, text="Add Book", command=add_book)
add_button.grid(row=4, column=0)

search_button = tk.Button(root, text="Search Book", command=search_books)
search_button.grid(row=4, column=1)

show_all_button = tk.Button(root, text="Show All Books", command=fetch_all_books)
show_all_button.grid(row=5, column=0)

delete_button = tk.Button(root, text="Delete Book", command=delete_book)
delete_button.grid(row=5, column=1)

update_button = tk.Button(root, text="Update Book", command=update_book)
update_button.grid(row=6, column=0)

clear_button = tk.Button(root, text="Clear Fields", command=clear_fields)
clear_button.grid(row=6, column=1)

# Create Listbox and Scrollbar
listbox = tk.Listbox(root, height=10, width=50)
listbox.grid(row=7, column=0, columnspan=2, rowspan=6)

scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=7, column=2, rowspan=6)

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Run the application
root.mainloop()
