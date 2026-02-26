# mess.py
import tkinter as tk
import random

class ChaosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Destroyer")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self.running = False

        self.label = tk.Label(root, text="Press Start Chaos.\nGood luck focusing.",
                              font=("Segoe UI", 14))
        self.label.pack(pady=30)

        self.start_btn = tk.Button(root, text="Start Chaos", command=self.start_chaos,
                                   font=("Segoe UI", 11), width=15)
        self.start_btn.pack()

        self.stop_btn = tk.Button(root, text="Stop Chaos", command=self.stop_chaos,
                                  font=("Segoe UI", 11), width=15, state="disabled")
        self.stop_btn.pack(pady=10)

    def start_chaos(self):
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.move_window()

    def stop_chaos(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def move_window(self):
        if not self.running:
            return

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 400
        window_height = 200

        x = random.randint(0, screen_width - window_width)
        y = random.randint(0, screen_height - window_height)

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # move again after short delay
        self.root.after(100, self.move_window)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChaosApp(root)
    root.mainloop()
