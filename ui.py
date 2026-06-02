import customtkinter as ctk
import threading
import math
import time

# ── State ────────────────────────────────────────────────
# States: sleeping, listening, thinking, speaking
current_state = "sleeping"

class JarvisUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("")
        self.root.geometry("200x200")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)        # always on top
        self.root.attributes('-alpha', 1.0)       # slightly transparent
        self.root.overrideredirect(True)              # no title bar
        self.root.configure(fg_color="#0a0a0a")

        # Position bottom right corner
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"200x200+{sw//2-100}+{sh//2-100}")

        # Canvas for drawing the orb
        self.canvas = ctk.CTkCanvas(
            self.root,
            width=200,
            height=200,
            bg="#0a0a0a",
            highlightthickness=0
        )
        self.canvas.pack()

        # Status label
        self.label = ctk.CTkLabel(
            self.root,
            text="Sleeping",
            font=("Arial", 11),
            text_color="#555555"
        )
        self.label.place(relx=0.5, rely=0.85, anchor="center")

        # Make window draggable
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)

        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.animate()

    def start_drag(self, e):
        self.x = e.x
        self.y = e.y

    def drag(self, e):
        dx = e.x - self.x
        dy = e.y - self.y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def animate(self):
        global current_state
        self.canvas.delete("all")

        cx, cy, r = 100, 95, 60

        if current_state == "sleeping":
            # Slow dim pulse — grey
            self.pulse += 0.03 * self.pulse_dir
            if self.pulse > 1 or self.pulse < 0:
                self.pulse_dir *= -1
            alpha_r = int(60 + 30 * self.pulse)
            color = f"#{alpha_r:02x}{alpha_r:02x}{alpha_r:02x}"
            self.canvas.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                fill=color, outline=""
            )
            # Outer glow
            self.canvas.create_oval(
                cx-r-8, cy-r-8, cx+r+8, cy+r+8,
                fill="", outline="#333333", width=1
            )
            self.label.configure(text="Sleeping", text_color="#555555")

        elif current_state == "listening":
            # Fast blue pulse — listening for command
            self.pulse += 0.08 * self.pulse_dir
            if self.pulse > 1 or self.pulse < 0:
                self.pulse_dir *= -1
            size = r + 10 * self.pulse
            self.canvas.create_oval(
                cx-size-10, cy-size-10, cx+size+10, cy+size+10,
                fill="", outline="#1a3a5c", width=2
            )
            self.canvas.create_oval(
                cx-size, cy-size, cx+size, cy+size,
                fill="#2E75B6", outline=""
            )
            self.label.configure(text="Listening...", text_color="#2E75B6")

        elif current_state == "thinking":
            # Rotating arc — thinking
            self.angle = (self.angle + 8) % 360
            self.canvas.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                fill="#1a1a2e", outline=""
            )
            # Rotating dots
            for i in range(8):
                a = math.radians(self.angle + i * 45)
                dx = (r - 8) * math.cos(a)
                dy = (r - 8) * math.sin(a)
                size = 4 if i == 0 else 2
                opacity = 255 - i * 28
                c = f"#{opacity:02x}{opacity//2:02x}00"
                self.canvas.create_oval(
                    cx+dx-size, cy+dy-size,
                    cx+dx+size, cy+dy+size,
                    fill=c, outline=""
                )
            self.label.configure(text="Thinking...", text_color="#F9A825")

        elif current_state == "speaking":
            # Green breathing — speaking
            self.pulse += 0.06 * self.pulse_dir
            if self.pulse > 1 or self.pulse < 0:
                self.pulse_dir *= -1
            size = r + 12 * self.pulse
            self.canvas.create_oval(
                cx-size-6, cy-size-6, cx+size+6, cy+size+6,
                fill="", outline="#1D7874", width=1
            )
            self.canvas.create_oval(
                cx-size, cy-size, cx+size, cy+size,
                fill="#1D9E75", outline=""
            )
            # Sound wave lines
            for i in range(3):
                wave_r = size + 15 + i * 10
                opacity = 80 - i * 25
                c = f"#00{opacity:02x}{opacity//2:02x}"
                self.canvas.create_oval(
                    cx-wave_r, cy-wave_r, cx+wave_r, cy+wave_r,
                    fill="", outline=f"#00{opacity+50:02x}50", width=1
                )
            self.label.configure(text="Speaking...", text_color="#1D9E75")

        self.root.after(30, self.animate)

    def run(self):
        self.root.mainloop()


def set_state(state):
    global current_state
    current_state = state


def start_ui():
    ui = JarvisUI()
    ui.run()