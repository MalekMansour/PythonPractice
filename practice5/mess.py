# mess.py
import json
import os
import time
import tkinter as tk
from tkinter import colorchooser, messagebox

SAVE_FILE = "mess_save.json"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class CookieClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Cookie Clicker (Fast & Satisfying)")
        self.root.geometry("520x620")
        self.root.resizable(False, False)

        self.money = 0.0

        self.base_click = 1.0
        self.multiplier = 1.0

        self.auto_owned = False
        self.auto_interval = 10.0
        self.auto_min_interval = 0.001 
        self.auto_speed_factor = 0.88  

        # Rebalanced costs (fast + satisfying)
        self.click_upgrade_cost = 15.0
        self.multiplier_cost = 25.0
        self.auto_cost = 40.0

        self.click_cost_scale = 1.28
        self.multiplier_cost_scale = 1.33
        self.auto_cost_scale = 1.38

        # Background color
        self.bg_color = "#1f1f24"

        # UI pulse state
        self.pulse_on = False

        # Auto timing
        self._last_time = time.perf_counter()
        self._auto_accumulator = 0.0

        # ---------- UI ----------
        self.root.configure(bg=self.bg_color)

        self.title_label = tk.Label(
            root, text="🍪 Cookie Clicker",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color, fg="white"
        )
        self.title_label.pack(pady=(14, 6))

        self.money_label = tk.Label(
            root, text="",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_color, fg="white",
            justify="center"
        )
        self.money_label.pack(pady=(6, 12))

        self.click_button = tk.Button(
            root, text="🍪 CLICK",
            font=("Segoe UI", 16, "bold"),
            width=18, height=2,
            command=self.click,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=4
        )
        self.click_button.pack(pady=10)

        # Upgrades header
        self.upg_label = tk.Label(
            root, text="Upgrades",
            font=("Segoe UI", 14, "bold"),
            bg=self.bg_color, fg="white"
        )
        self.upg_label.pack(pady=(18, 8))

        # Upgrade buttons
        self.btn_click = tk.Button(
            root, text="", font=("Segoe UI", 12),
            command=self.buy_click_upgrade,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=3
        )
        self.btn_click.pack(pady=6, ipadx=6, ipady=4)

        self.btn_mult = tk.Button(
            root, text="", font=("Segoe UI", 12),
            command=self.buy_multiplier,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=3
        )
        self.btn_mult.pack(pady=6, ipadx=6, ipady=4)

        self.btn_auto = tk.Button(
            root, text="", font=("Segoe UI", 12),
            command=self.buy_auto,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=3
        )
        self.btn_auto.pack(pady=6, ipadx=6, ipady=4)

        # Utility row
        self.util_frame = tk.Frame(root, bg=self.bg_color)
        self.util_frame.pack(pady=(18, 0))

        self.btn_bg = tk.Button(
            self.util_frame, text="🎨 Background Color",
            font=("Segoe UI", 11),
            command=self.pick_bg_color,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=2
        )
        self.btn_bg.grid(row=0, column=0, padx=6, pady=6)

        self.btn_save = tk.Button(
            self.util_frame, text="💾 Save",
            font=("Segoe UI", 11),
            command=self.save_game,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=2
        )
        self.btn_save.grid(row=0, column=1, padx=6, pady=6)

        self.btn_load = tk.Button(
            self.util_frame, text="📂 Load",
            font=("Segoe UI", 11),
            command=self.load_game,
            bg="#2e2e38", fg="white",
            activebackground="#3a3a48", activeforeground="white",
            relief="raised", bd=2
        )
        self.btn_load.grid(row=0, column=2, padx=6, pady=6)

        # Info tip
        self.tip_label = tk.Label(
            root,
            text="AutoClicker earns exactly what you earn per click.\nUpgrading it makes it click faster (down to 1ms).",
            font=("Segoe UI", 10),
            bg=self.bg_color, fg="#cfcfe6",
            justify="center"
        )
        self.tip_label.pack(pady=(18, 6))

        # Try loading on start (no popup if missing)
        self.load_game(silent=True)

        # Start loops
        self.update_ui()
        self.root.after(120, self.pulse_loop)
        self.root.after(30, self.auto_loop)   # simulate fast auto without 1ms spam

    # ---------- Core math ----------
    def click_value(self) -> float:
        return self.base_click * self.multiplier

    def format_money(self, x: float) -> str:
        # Fast clicker style: keep it readable
        if x < 1000:
            return f"${x:,.0f}"
        if x < 1_000_000:
            return f"${x/1000:,.2f}K"
        if x < 1_000_000_000:
            return f"${x/1_000_000:,.2f}M"
        return f"${x/1_000_000_000:,.2f}B"

    # ---------- UI text ----------
    def money_text(self) -> str:
        auto_text = "Not owned"
        if self.auto_owned:
            ms = self.auto_interval * 1000.0
            if self.auto_interval <= self.auto_min_interval + 1e-12:
                auto_text = "MAX speed (1ms)"
            else:
                auto_text = f"Every {ms:.2f} ms"
        return (
            f"Money: {self.format_money(self.money)}\n"
            f"Per Click: {self.format_money(self.click_value())}  (Base {self.base_click:.0f} × x{self.multiplier:.0f})\n"
            f"AutoClicker: {auto_text}"
        )

    def btn_texts(self):
        t1 = f"💪 Upgrade Click Power  (+1 Base)   Cost: {self.format_money(self.click_upgrade_cost)}"
        t2 = f"🔼 Upgrade Multiplier   (+1x)      Cost: {self.format_money(self.multiplier_cost)}"

        if not self.auto_owned:
            t3 = f"🤖 Buy AutoClicker (starts 10s)    Cost: {self.format_money(self.auto_cost)}"
        else:
            if self.auto_interval <= self.auto_min_interval + 1e-12:
                t3 = "🤖 AutoClicker MAX speed (1ms)"
            else:
                nxt = max(self.auto_min_interval, self.auto_interval * self.auto_speed_factor)
                t3 = f"🤖 Upgrade AutoClicker ({self.auto_interval:.3f}s → {nxt:.3f}s)  Cost: {self.format_money(self.auto_cost)}"
        return t1, t2, t3

    # ---------- Glow / Pulse ----------
    def set_button_style(self, btn: tk.Button, affordable: bool, disabled: bool = False):
        if disabled:
            btn.config(state="disabled", bg="#24242b", fg="#777", relief="sunken")
            return

        btn.config(state="normal", relief="raised")

        if affordable:
            # pulse between two bright colors
            if self.pulse_on:
                btn.config(bg="#ffd54a", fg="#1a1a1a")  # bright
            else:
                btn.config(bg="#ffb300", fg="#1a1a1a")  # slightly darker
        else:
            btn.config(bg="#2e2e38", fg="white")

    def pulse_loop(self):
        self.pulse_on = not self.pulse_on
        self.update_ui()
        self.root.after(180, self.pulse_loop)

    # ---------- UI update ----------
    def update_ui(self):
        self.money_label.config(text=self.money_text())

        t1, t2, t3 = self.btn_texts()
        self.btn_click.config(text=t1)
        self.btn_mult.config(text=t2)
        self.btn_auto.config(text=t3)

        # affordability checks
        can_click = self.money >= self.click_upgrade_cost
        can_mult = self.money >= self.multiplier_cost

        auto_disabled = self.auto_owned and (self.auto_interval <= self.auto_min_interval + 1e-12)
        can_auto = (not auto_disabled) and (self.money >= self.auto_cost)

        self.set_button_style(self.btn_click, can_click)
        self.set_button_style(self.btn_mult, can_mult)
        self.set_button_style(self.btn_auto, can_auto, disabled=auto_disabled)

        # autosave quietly
        self.autosave()

    # ---------- Actions ----------
    def click(self):
        self.money += self.click_value()
        self.update_ui()

    def buy_click_upgrade(self):
        if self.money < self.click_upgrade_cost:
            return
        self.money -= self.click_upgrade_cost
        self.base_click += 1
        self.click_upgrade_cost = max(1.0, self.click_upgrade_cost * self.click_cost_scale)
        self.update_ui()

    def buy_multiplier(self):
        if self.money < self.multiplier_cost:
            return
        self.money -= self.multiplier_cost
        self.multiplier += 1
        self.multiplier_cost = max(1.0, self.multiplier_cost * self.multiplier_cost_scale)
        self.update_ui()

    def buy_auto(self):
        # Maxed
        if self.auto_owned and (self.auto_interval <= self.auto_min_interval + 1e-12):
            return
        if self.money < self.auto_cost:
            return

        self.money -= self.auto_cost

        if not self.auto_owned:
            self.auto_owned = True
            self.auto_interval = 10.0
            self._auto_accumulator = 0.0
        else:
            self.auto_interval = max(self.auto_min_interval, self.auto_interval * self.auto_speed_factor)

        self.auto_cost = max(1.0, self.auto_cost * self.auto_cost_scale)
        self.update_ui()

    # ---------- Auto simulation loop (handles 1ms cap without spamming callbacks) ----------
    def auto_loop(self):
        now = time.perf_counter()
        dt = now - self._last_time
        self._last_time = now

        if self.auto_owned:
            self._auto_accumulator += dt

            # how many auto-clicks should happen this frame?
            interval = max(self.auto_min_interval, self.auto_interval)

            # cap the loop so the UI doesn't freeze if someone goes insane fast
            max_clicks_per_frame = 2000

            clicks = int(self._auto_accumulator // interval)
            if clicks > 0:
                clicks = min(clicks, max_clicks_per_frame)
                self._auto_accumulator -= clicks * interval
                self.money += clicks * self.click_value()
                self.update_ui()

        self.root.after(30, self.auto_loop)

    # ---------- Save / Load ----------
    def autosave(self):
        # silent autosave (no popup)
        try:
            data = self._serialize()
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def save_game(self):
        try:
            data = self._serialize()
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", f"Saved to {SAVE_FILE}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def load_game(self, silent=False):
        if not os.path.exists(SAVE_FILE):
            if not silent:
                messagebox.showinfo("No save found", f"No {SAVE_FILE} found yet.")
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._apply_save(data)
            self.update_ui()
            if not silent:
                messagebox.showinfo("Loaded", "Save loaded!")
        except Exception as e:
            if not silent:
                messagebox.showerror("Load failed", str(e))

    def _serialize(self):
        return {
            "money": self.money,
            "base_click": self.base_click,
            "multiplier": self.multiplier,
            "auto_owned": self.auto_owned,
            "auto_interval": self.auto_interval,
            "click_upgrade_cost": self.click_upgrade_cost,
            "multiplier_cost": self.multiplier_cost,
            "auto_cost": self.auto_cost,
            "bg_color": self.bg_color,
        }

    def _apply_save(self, data):
        self.money = float(data.get("money", self.money))
        self.base_click = float(data.get("base_click", self.base_click))
        self.multiplier = float(data.get("multiplier", self.multiplier))

        self.auto_owned = bool(data.get("auto_owned", self.auto_owned))
        self.auto_interval = float(data.get("auto_interval", self.auto_interval))
        self.auto_interval = max(self.auto_min_interval, self.auto_interval)

        self.click_upgrade_cost = float(data.get("click_upgrade_cost", self.click_upgrade_cost))
        self.multiplier_cost = float(data.get("multiplier_cost", self.multiplier_cost))
        self.auto_cost = float(data.get("auto_cost", self.auto_cost))

        self.bg_color = str(data.get("bg_color", self.bg_color))
        self.apply_bg_color(self.bg_color)

    # ---------- Background color ----------
    def pick_bg_color(self):
        chosen = colorchooser.askcolor(title="Pick background color")
        if not chosen or not chosen[1]:
            return
        self.bg_color = chosen[1]
        self.apply_bg_color(self.bg_color)
        self.update_ui()

    def apply_bg_color(self, color_hex: str):
        self.root.configure(bg=color_hex)
        for w in [self.title_label, self.money_label, self.upg_label, self.tip_label, self.util_frame]:
            try:
                w.configure(bg=color_hex)
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CookieClicker(root)
    root.mainloop()
