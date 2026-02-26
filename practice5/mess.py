# mess.py
import tkinter as tk

class CookieClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Cookie Empire")
        self.root.geometry("450x520")
        self.root.resizable(False, False)

        # Game state
        self.money = 0
        self.base_click = 1
        self.multiplier = 1
        self.auto_income = 0

        self.multiplier_cost = 50
        self.auto_cost = 100
        self.click_upgrade_cost = 75

        # Money display
        self.money_label = tk.Label(root, text=self.money_text(),
                                    font=("Segoe UI", 16, "bold"))
        self.money_label.pack(pady=10)

        # Click button
        self.click_button = tk.Button(root, text="🍪 Click",
                                      font=("Segoe UI", 16),
                                      width=18, height=2,
                                      command=self.click)
        self.click_button.pack(pady=15)

        tk.Label(root, text="Upgrades",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Stronger Click upgrade
        self.click_upgrade_button = tk.Button(
            root,
            text=self.click_upgrade_text(),
            command=self.buy_click_upgrade
        )
        self.click_upgrade_button.pack(pady=5)

        # Multiplier upgrade
        self.multiplier_button = tk.Button(
            root,
            text=self.multiplier_text(),
            command=self.buy_multiplier
        )
        self.multiplier_button.pack(pady=5)

        # Auto clicker
        self.auto_button = tk.Button(
            root,
            text=self.auto_text(),
            command=self.buy_auto
        )
        self.auto_button.pack(pady=5)

        self.auto_loop()

    # ---------- TEXT HELPERS ----------

    def money_text(self):
        return (f"Money: ${self.money}\n"
                f"Base Click: ${self.base_click} | "
                f"Multiplier: x{self.multiplier}")

    def click_upgrade_text(self):
        return f"Upgrade Click Power (+$1 base) (Cost: ${self.click_upgrade_cost})"

    def multiplier_text(self):
        return f"Upgrade Multiplier (Cost: ${self.multiplier_cost})"

    def auto_text(self):
        return f"Buy Auto Clicker (+$1/sec) (Cost: ${self.auto_cost})"

    def update_ui(self):
        self.money_label.config(text=self.money_text())
        self.click_upgrade_button.config(text=self.click_upgrade_text())
        self.multiplier_button.config(text=self.multiplier_text())
        self.auto_button.config(text=self.auto_text())

    # ---------- GAME LOGIC ----------

    def click(self):
        earned = self.base_click * self.multiplier
        self.money += earned
        self.update_ui()

    def buy_click_upgrade(self):
        if self.money >= self.click_upgrade_cost:
            self.money -= self.click_upgrade_cost
            self.base_click += 1
            self.click_upgrade_cost = int(self.click_upgrade_cost * 1.7)
            self.update_ui()

    def buy_multiplier(self):
        if self.money >= self.multiplier_cost:
            self.money -= self.multiplier_cost
            self.multiplier += 1
            self.multiplier_cost = int(self.multiplier_cost * 1.8)
            self.update_ui()

    def buy_auto(self):
        if self.money >= self.auto_cost:
            self.money -= self.auto_cost
            self.auto_income += 1
            self.auto_cost = int(self.auto_cost * 2)
            self.update_ui()

    def auto_loop(self):
        self.money += self.auto_income
        self.update_ui()
        self.root.after(1000, self.auto_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = CookieClicker(root)
    root.mainloop()
