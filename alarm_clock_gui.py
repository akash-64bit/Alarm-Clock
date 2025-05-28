import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
import time
import threading
import os
import pygame
import math

# Initialize pygame mixer
pygame.mixer.init()

# Helper functions
def play_alarm(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)

def stop_alarm():
    pygame.mixer.music.stop()

def fade_alarm():
    pygame.mixer.music.fadeout(2000)

def save_alarm_history(message):
    with open("alarm_history.txt", "a") as file:
        file.write(f"{datetime.datetime.now()} - {message}\n")

class Alarm:
    def __init__(self, time_str, snooze, tone):
        self.time_str = time_str
        self.snooze = snooze
        self.tone = tone
        self.time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
        self.active = True

class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Alarm Clock")
        self.root.geometry("460x600")
        self.root.configure(bg="#121212")

        self.alarms = []

        # Digital Clock
        self.clock_label = tk.Label(root, font=("Helvetica", 32), fg="white", bg="#121212")
        self.clock_label.pack(pady=10)
        self.update_clock()

        # Analog Clock
        self.canvas = tk.Canvas(root, width=200, height=200, bg="#121212", highlightthickness=0)
        self.canvas.pack()
        self.draw_clock_face()
        self.update_analog_clock()

        # Alarm Input Section
        tk.Label(root, text="Set Alarm (HH:MM)", fg="white", bg="#121212").pack(pady=5)
        self.time_entry = tk.Entry(root, font=("Helvetica", 14))
        self.time_entry.pack()

        tk.Label(root, text="Snooze (minutes)", fg="white", bg="#121212").pack(pady=5)
        self.snooze_entry = tk.Entry(root, font=("Helvetica", 14))
        self.snooze_entry.insert(0, "5")
        self.snooze_entry.pack()

        self.tone_btn = tk.Button(root, text="Choose Alarm Tone", command=self.choose_tone, bg="#333", fg="white")
        self.tone_btn.pack(pady=5)
        self.tone_label = tk.Label(root, text="No tone selected", fg="gray", bg="#121212")
        self.tone_label.pack()

        self.add_alarm_btn = tk.Button(root, text="Add Alarm", command=self.add_alarm, bg="#1E88E5", fg="white")
        self.add_alarm_btn.pack(pady=10)

        # Alarm List
        self.alarm_listbox = tk.Listbox(root, bg="#1e1e1e", fg="white", font=("Courier", 12), height=6)
        self.alarm_listbox.pack(pady=10)
        self.remove_btn = tk.Button(root, text="Remove Selected Alarm", command=self.remove_alarm, bg="red", fg="white")
        self.remove_btn.pack()

        # Start background checker
        threading.Thread(target=self.check_alarms, daemon=True).start()

        self.selected_tone = None

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def draw_clock_face(self):
        self.canvas.create_oval(10, 10, 190, 190, outline="white", width=2)
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = 100 + 80 * math.sin(angle)
            y1 = 100 - 80 * math.cos(angle)
            x2 = 100 + 90 * math.sin(angle)
            y2 = 100 - 90 * math.cos(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

    def update_analog_clock(self):
        self.canvas.delete("hands")
        now = datetime.datetime.now()
        second = now.second
        minute = now.minute
        hour = now.hour % 12 + minute / 60

        sec_angle = math.radians(second * 6)
        min_angle = math.radians(minute * 6)
        hour_angle = math.radians(hour * 30)

        self.draw_hand(hour_angle, 50, "white", 4)
        self.draw_hand(min_angle, 70, "white", 3)
        self.draw_hand(sec_angle, 80, "red", 2)

        self.root.after(1000, self.update_analog_clock)

    def draw_hand(self, angle, length, color, width):
        x = 100 + length * math.sin(angle)
        y = 100 - length * math.cos(angle)
        self.canvas.create_line(100, 100, x, y, fill=color, width=width, tags="hands")

    def choose_tone(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if path:
            self.selected_tone = path
            self.tone_label.config(text=os.path.basename(path))

    def add_alarm(self):
        time_str = self.time_entry.get()
        try:
            snooze = int(self.snooze_entry.get())
            if not self.selected_tone:
                messagebox.showwarning("Missing Tone", "Select an alarm tone.")
                return
            alarm = Alarm(time_str, snooze, self.selected_tone)
            self.alarms.append(alarm)
            self.alarm_listbox.insert(tk.END, f"{time_str} | Snooze: {snooze} min")
            messagebox.showinfo("Alarm Added", f"Alarm set for {time_str}")
        except ValueError:
            messagebox.showerror("Error", "Enter time in HH:MM and snooze as a number.")

    def remove_alarm(self):
        idx = self.alarm_listbox.curselection()
        if idx:
            self.alarm_listbox.delete(idx)
            self.alarms.pop(idx[0])
            messagebox.showinfo("Alarm Removed", "Alarm deleted.")

    def check_alarms(self):
        while True:
            now = datetime.datetime.now().time()
            for alarm in self.alarms:
                if alarm.active and now.hour == alarm.time_obj.hour and now.minute == alarm.time_obj.minute:
                    alarm.active = False  # Prevent repeat
                    self.trigger_alarm(alarm)
            time.sleep(10)

    def trigger_alarm(self, alarm):
        play_alarm(alarm.tone)
        save_alarm_history(f"ALARM RANG at {alarm.time_str}")
        while True:
            choice = messagebox.askquestion("Alarm", f"Alarm {alarm.time_str} - Snooze or Stop?", icon='question')
            if choice == 'yes':  # Snooze
                stop_alarm()
                save_alarm_history(f"SNOOZED {alarm.time_str} for {alarm.snooze} mins")
                time.sleep(alarm.snooze * 60)
                play_alarm(alarm.tone)
            else:
                fade_alarm()
                save_alarm_history(f"STOPPED {alarm.time_str}")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClockApp(root)
    root.mainloop()
