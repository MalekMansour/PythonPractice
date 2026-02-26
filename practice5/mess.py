# mess.py
import tkinter as tk
from tkinter import ttk, messagebox
import random

TEMPLATES = [
    "⚠️ {name}, your vibe just triggered a system reboot.",
    "🧨 {name} accidentally opened 37 tabs and called it productivity.",
    "🌀 {name} is currently being chased by thoughts at 120mph.",
    "📡 {name} sent a signal into the void and the void replied: 'lol'.",
    "🧊 {name} tried to stay calm but the microwave beeped once.",
    "🎭 {name} has two moods: dramatic silence and chaotic confession.",
    "🕳️ {name} fell into a rabbit hole and came back with screenshots.",
    "🔮 {name}'s future is unclear, but it's definitely loud.",
    "🧃 {name} is running on iced coffee and poor decisions.",
    "🧠 {name} brain status: buffering… 99%… buffering…",
]

EMOJIS = ["💥", "😵‍💫", "🧟", "🔥", "🧠", "👁️", "🪩", "🫠", "🧃", "⚡"]

def generate_message():
    name = name_var.get().strip()
    if not name:
        name = "Bestie"

    msg = random.choice(TEMPLATES).format(name=name)
    if emoji_var.get():
        msg = f"{random.choice(EMOJIS)} {msg}"

    output_var.set(msg)

def copy_to_clipboard():
    msg = output_var.get().strip()
    if not msg:
        messagebox.showinfo("Nothing to copy", "Generate a message first.")
        return
    root.clipboard_clear()
    root.clipboard_append(msg)
    root.update()
    messagebox.showinfo("Copied", "Message copied to clipboard.")

def clear_all():
    name_var.set("")
    output_var.set("")

root = tk.Tk()
root.title("Mess Generator")
root.geometry("520x260")
root.minsize(520, 260)

style = ttk.Style(root)
try:
    style.theme_use("clam")
except:
    pass

# Variables
name_var = tk.StringVar()
output_var = tk.StringVar(value="")
emoji_var = tk.BooleanVar(value=True)

# Layout
main = ttk.Frame(root, padding=14)
main.pack(fill="both", expand=True)

title = ttk.Label(main, text="Mess Generator", font=("Segoe UI", 16, "bold"))
title.pack(anchor="w")

subtitle = ttk.Label(main, text="Type a name → generate one chaotic message.", font=("Segoe UI", 10))
subtitle.pack(anchor="w", pady=(2, 10))

row1 = ttk.Frame(main)
row1.pack(fill="x")

ttk.Label(row1, text="Name:").pack(side="left")
entry = ttk.Entry(row1, textvariable=name_var)
entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
entry.focus()

row2 = ttk.Frame(main)
row2.pack(fill="x", pady=(10, 0))

ttk.Checkbutton(row2, text="Add extra emoji", variable=emoji_var).pack(side="left")

row3 = ttk.Frame(main)
row3.pack(fill="x", pady=(12, 0))

ttk.Label(row3, text="Output:").pack(anchor="w")

output_box = ttk.Entry(row3, textvariable=output_var, state="readonly")
output_box.pack(fill="x", pady=(6, 0))

buttons = ttk.Frame(main)
buttons.pack(fill="x", pady=(14, 0))

gen_btn = ttk.Button(buttons, text="Generate Mess", command=generate_message)
gen_btn.pack(side="left")

copy_btn = ttk.Button(buttons, text="Copy", command=copy_to_clipboard)
copy_btn.pack(side="left", padx=8)

clear_btn = ttk.Button(buttons, text="Clear", command=clear_all)
clear_btn.pack(side="left")

# Enter key generates
root.bind("<Return>", lambda e: generate_message())

root.mainloop()
