# mess.py
import tkinter as tk

def do_nothing():
    pass  # literally does nothing

root = tk.Tk()
root.title("Nothing App")
root.geometry("300x200")
root.resizable(False, False)

button = tk.Button(
    root,
    text="Click Me",
    font=("Segoe UI", 12),
    command=do_nothing
)

button.pack(expand=True)

root.mainloop()
