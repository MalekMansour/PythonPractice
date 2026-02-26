# mess.py
import tkinter as tk
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple To-Do List")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        # Title
        title = tk.Label(root, text="My To-Do List", font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        # Entry field
        self.task_entry = tk.Entry(root, font=("Segoe UI", 12))
        self.task_entry.pack(pady=10, padx=20, fill="x")

        # Add button
        add_btn = tk.Button(root, text="Add Task", command=self.add_task)
        add_btn.pack(pady=5)

        # Listbox
        self.task_listbox = tk.Listbox(root, font=("Segoe UI", 12), selectmode=tk.SINGLE)
        self.task_listbox.pack(pady=15, padx=20, fill="both", expand=True)

        # Delete button
        delete_btn = tk.Button(root, text="Delete Selected Task", command=self.delete_task)
        delete_btn.pack(pady=5)

        # Enter key adds task
        root.bind("<Return>", lambda event: self.add_task())

    def add_task(self):
        task = self.task_entry.get().strip()
        if task == "":
            messagebox.showwarning("Warning", "Task cannot be empty.")
            return
        self.task_listbox.insert(tk.END, task)
        self.task_entry.delete(0, tk.END)

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        self.task_listbox.delete(selected[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
