import customtkinter as ctk
import threading
import math
import time

current_state = "sleeping"

class JarvisUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.title("")
        self.root.geometry("280x280")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        self.root.overrideredirect(True)
        self.root.configure(fg_color="#050510")

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw // 2 - 140
        y = sh // 2 - 140
        self.root.geometry(f"280x280+{x}+{y}")

        # Canvas
        self.canvas = ctk.CTkCanvas(
            self.root,
            width=280,
            height=280,
            bg="#050510",
            highlightthickness=0
        )
        self.canvas.pack()

        # Status label
        self.label = ctk.CTkLabel(
            self.root,
            text="SLEEPING",
            font=("Helvetica", 10, "bold"),
            text_color="#333355",
            fg_color="transparent"
        )
        self.label.place(relx=0.5, rely=0.88, anchor="center")

        # Name label
        self.name_label = ctk.CTkLabel(
            self.root,
            text="J.A.R.V.I.S",
            font=("Helvetica", 11, "bold"),
            text_color="#222244",
            fg_color="transparent"
        )
        self.name_label.place(relx=0.5, rely=0.94, anchor="center")

        # Drag support
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)

        # Close on double click
        self.canvas.bind("<Double-Button-1>", lambda e: None)

        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.ring_angle = 0
        self.frame = 0
        self.animate()

    def start_drag(self, e):
        self._x = e.x
        self._y = e.y

    def drag(self, e):
        dx = e.x - self._x
        dy = e.y - self._y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def draw_ring(self, cx, cy, r, color, width=1, dash=None):
        if dash:
            self.canvas.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                outline=color, width=width
            )
        else:
            self.canvas.create_oval(
                cx-r, cy-r, cx+r, cy+r,
                outline=color, width=width
            )

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, r, g, b):
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return f'#{r:02x}{g:02x}{b:02x}'

    def animate(self):
        global current_state
        self.canvas.delete("all")
        self.frame += 1

        cx, cy = 140, 130
        self.pulse += 0.04 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1
        self.ring_angle = (self.ring_angle + 2) % 360

        if current_state == "sleeping":
            # Dark blue dim pulse
            r = 55 + int(15 * self.pulse)
            core_color = self.rgb_to_hex(5, 5, r)
            glow_color = self.rgb_to_hex(10, 10, 80 + int(20 * self.pulse))

            # Outer rings — barely visible
            self.draw_ring(cx, cy, 100, "#0a0a2a", 1)
            self.draw_ring(cx, cy, 85, "#0d0d35", 1)
            self.draw_ring(cx, cy, 70, "#0f0f40", 1)

            # Core
            self.canvas.create_oval(
                cx-50, cy-50, cx+50, cy+50,
                fill=core_color, outline=glow_color, width=1
            )
            # Inner glow
            self.canvas.create_oval(
                cx-25, cy-25, cx+25, cy+25,
                fill=self.rgb_to_hex(15, 15, 100 + int(30 * self.pulse)),
                outline=""
            )
            self.label.configure(text="SLEEPING", text_color="#1a1a4a")
            self.name_label.configure(text_color="#111133")

        elif current_state == "listening":
            # Electric blue — pulsing fast
            self.pulse += 0.04
            intensity = abs(math.sin(self.frame * 0.15))

            # Outer glow rings
            for i, (rad, alpha) in enumerate([(110, 0.1), (95, 0.2), (80, 0.35)]):
                a = int(255 * alpha * intensity)
                c = self.rgb_to_hex(0, int(100 * alpha), 255)
                self.draw_ring(cx, cy, rad, c, width=1 + i)

            # Rotating arc indicator
            for i in range(12):
                a = math.radians(self.ring_angle + i * 30)
                x1 = cx + 65 * math.cos(a)
                y1 = cy + 65 * math.sin(a)
                size = 3 if i == 0 else 1
                bright = 255 - i * 18
                color = self.rgb_to_hex(0, bright // 2, bright)
                self.canvas.create_oval(
                    x1-size, y1-size, x1+size, y1+size,
                    fill=color, outline=""
                )

            # Core
            core_b = int(180 + 75 * intensity)
            self.canvas.create_oval(
                cx-55, cy-55, cx+55, cy+55,
                fill=self.rgb_to_hex(0, 50, 150),
                outline=self.rgb_to_hex(0, 150, 255), width=2
            )
            self.canvas.create_oval(
                cx-30, cy-30, cx+30, cy+30,
                fill=self.rgb_to_hex(0, 100, core_b),
                outline=""
            )
            # Center dot
            self.canvas.create_oval(
                cx-8, cy-8, cx+8, cy+8,
                fill="#ffffff", outline=""
            )
            self.label.configure(text="LISTENING", text_color="#00aaff")
            self.name_label.configure(text_color="#0066cc")

        elif current_state == "thinking":
            # Gold spinning — thinking
            self.ring_angle = (self.ring_angle + 6) % 360

            # Background rings
            self.draw_ring(cx, cy, 100, "#1a1000", 1)
            self.draw_ring(cx, cy, 85, "#251500", 1)

            # Spinning particles
            for i in range(16):
                a = math.radians(self.ring_angle + i * 22.5)
                rad = 70 + 10 * math.sin(math.radians(i * 45 + self.frame * 3))
                x1 = cx + rad * math.cos(a)
                y1 = cy + rad * math.sin(a)
                size = 4 if i % 4 == 0 else 2
                bright = 255 - i * 12
                color = self.rgb_to_hex(bright, int(bright * 0.7), 0)
                self.canvas.create_oval(
                    x1-size, y1-size, x1+size, y1+size,
                    fill=color, outline=""
                )

            # Inner spinning ring
            for i in range(8):
                a = math.radians(-self.ring_angle * 2 + i * 45)
                x1 = cx + 45 * math.cos(a)
                y1 = cy + 45 * math.sin(a)
                color = self.rgb_to_hex(255, 180 - i * 15, 0)
                self.canvas.create_oval(
                    x1-3, y1-3, x1+3, y1+3,
                    fill=color, outline=""
                )

            # Core
            self.canvas.create_oval(
                cx-30, cy-30, cx+30, cy+30,
                fill="#1a0f00",
                outline="#ffaa00", width=2
            )
            self.canvas.create_oval(
                cx-12, cy-12, cx+12, cy+12,
                fill="#ff8800", outline=""
            )
            self.label.configure(text="THINKING", text_color="#ffaa00")
            self.name_label.configure(text_color="#cc7700")

        elif current_state == "speaking":
            # Green breathing waves
            intensity = abs(math.sin(self.frame * 0.12))

            # Sound wave rings
            for i in range(5):
                rad = 50 + i * 13 + int(8 * intensity)
                alpha = 1.0 - i * 0.18
                g = int(200 * alpha * (0.5 + 0.5 * intensity))
                b = int(120 * alpha)
                c = self.rgb_to_hex(0, g, b)
                self.draw_ring(cx, cy, rad, c, width=2 - (i > 2))

            # Rotating outer ring
            for i in range(20):
                a = math.radians(self.ring_angle * 1.5 + i * 18)
                x1 = cx + 95 * math.cos(a)
                y1 = cy + 95 * math.sin(a)
                bright = int(150 * (1 - i / 20))
                color = self.rgb_to_hex(0, bright, int(bright * 0.6))
                self.canvas.create_oval(
                    x1-2, y1-2, x1+2, y1+2,
                    fill=color, outline=""
                )

            # Core
            g_core = int(150 + 105 * intensity)
            self.canvas.create_oval(
                cx-50, cy-50, cx+50, cy+50,
                fill=self.rgb_to_hex(0, 80, 60),
                outline=self.rgb_to_hex(0, g_core, 120), width=2
            )
            self.canvas.create_oval(
                cx-25, cy-25, cx+25, cy+25,
                fill=self.rgb_to_hex(0, g_core, 100),
                outline=""
            )
            self.canvas.create_oval(
                cx-10, cy-10, cx+10, cy+10,
                fill="#00ffaa", outline=""
            )
            self.label.configure(text="SPEAKING", text_color="#00dd88")
            self.name_label.configure(text_color="#009955")

        self.root.after(30, self.animate)

    def run(self):
        self.root.mainloop()


def set_state(state):
    global current_state
    current_state = state


def start_ui():
    ui = JarvisUI()
    ui.run()