# mess.py
import tkinter as tk

class CookieClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Cookie Clicker")
        self.root.geometry("300x250")
        self.root.resizable(False, False)

        self.money = 0

        # Money label
        self.money_label = tk.Label(
            root,
            text=f"Money: ${self.money}",
            font=("Segoe UI", 16, "bold")
        )
        self.money_label.pack(pady=20)

        # Click button
        self.click_button = tk.Button(
            root,
            text="🍪 Click Me",
            font=("Segoe UI", 14),
            width=15,
            height=2,
            command=self.click
        )
        self.click_button.pack()

    def click(self):
        self.money += 1
        self.money_label.config(text=f"Money: ${self.money}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CookieClicker(root)
    root.mainloop()
