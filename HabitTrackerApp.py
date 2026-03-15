import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date, timedelta
import calendar
import threading

class HabitTrackerApp:
    def __init__(self, user, db_manager):
        self.user = user
        self.db_manager = db_manager
        self.habits = []
        self.current_habit_logs = {}
        self.current_month = date.today()
        self.root = tk.Tk()
        self.root.title("Habit Tracker - " + user.name)
        self.root.geometry("900x650")
        self.top_panel = tk.Frame(self.root)
        self.center_panel = tk.Frame(self.root)
        self.bottom_panel = tk.Frame(self.root)
        self.top_panel.pack(fill="x")
        self.center_panel.pack(fill="both", expand=True)
        self.bottom_panel.pack(fill="x")
        self.create_top_panel()
        self.create_center_panel()
        self.create_bottom_panel()
        self.load_habits()

    def create_top_panel(self):
        tk.Label(self.top_panel, text="User: " + self.user.name + " (@" + self.user.username + ")").pack(side="left")
        tk.Label(self.top_panel, text="Select Habit:").pack(side="left")
        self.habit_combo = ttk.Combobox(self.top_panel)
        self.habit_combo.pack(side="left")
        self.habit_combo.bind("<<ComboboxSelected>>", self.on_habit_selected)
        tk.Button(self.top_panel, text="New Habit", command=self.create_new_habit).pack(side="left")
        tk.Button(self.top_panel, text="< Prev Month", command=lambda: self.change_month(-1)).pack(side="left")
        tk.Button(self.top_panel, text="Next Month >", command=lambda: self.change_month(1)).pack(side="left")
        tk.Button(self.top_panel, text="Logout", command=self.logout).pack(side="left")

    def create_center_panel(self):
        self.header_panel = tk.Frame(self.center_panel)
        self.header_panel.pack(fill="x")
        self.year_label = tk.Label(self.header_panel, text=str(self.current_month.year), font=("Arial", 24))
        self.year_label.pack(side="top")
        self.month_label = tk.Label(self.header_panel, text=self.current_month.strftime("%B"), font=("Arial", 18))
        self.month_label.pack(side="top")
        self.calendar_panel = tk.Frame(self.center_panel)
        self.calendar_panel.pack(fill="both", expand=True)
        self.calendar_buttons = []
        for i in range(42):
            button = tk.Button(self.calendar_panel, text="", command=lambda i=i: self.on_day_clicked(i), height=3, width=10)
            button.grid(row=i//7, column=i%7)
            self.calendar_buttons.append(button)

    def create_bottom_panel(self):
        self.streak_label = tk.Label(self.bottom_panel, text="Current Streak: 0 days")
        self.streak_label.pack(side="left")
        tk.Button(self.bottom_panel, text="Export Report", command=self.export_report).pack(side="left")

    def load_habits(self):
        self.habits = self.db_manager.get_habits_for_user(self.user.id)
        self.habit_combo['values'] = [habit.name for habit in self.habits]
        if self.habits:
            self.habit_combo.set(self.habits[0].name)
            self.on_habit_selected(None)

    def on_habit_selected(self, event):
        selected_habit = next((habit for habit in self.habits if habit.name == self.habit_combo.get()), None)
        if selected_habit:
            self.current_habit_logs = self.db_manager.get_logs_for_habit(selected_habit.id)
            self.update_calendar()
            self.update_streak()

    def update_calendar(self):
        first_day_of_month = self.current_month.replace(day=1)
        days_in_month = calendar.monthrange(self.current_month.year, self.current_month.month)[1]
        first_day_of_week = first_day_of_month.weekday()
        today = date.today()
        self.year_label['text'] = str(self.current_month.year)
        self.month_label['text'] = self.current_month.strftime("%B")
        for i in range(42):
            self.calendar_buttons[i]['text'] = ""
            self.calendar_buttons[i]['bg'] = "lightgray"
            self.calendar_buttons[i]['state'] = "disabled"
        for day in range(1, days_in_month + 1):
            button_index = first_day_of_week + day - 1
            if button_index < 42:
                self.calendar_buttons[button_index]['text'] = str(day)
                date = self.current_month.replace(day=day)
                if date < today:
                    self.calendar_buttons[button_index]['state'] = "disabled"
                    self.calendar_buttons[button_index]['tooltip'] = "Past dates cannot be edited"
                else:
                    self.calendar_buttons[button_index]['state'] = "normal"
                    self.calendar_buttons[button_index]['tooltip'] = "Click to toggle completion"
                if date in self.current_habit_logs:
                    if self.current_habit_logs[date]:
                        self.calendar_buttons[button_index]['bg'] = "green"
                    else:
                        self.calendar_buttons[button_index]['bg'] = "red"
                else:
                    if date < today:
                        self.calendar_buttons[button_index]['bg'] = "gray"
                    else:
                        self.calendar_buttons[button_index]['bg'] = "white"

    def on_day_clicked(self, button_index):
        selected_habit = next((habit for habit in self.habits if habit.name == self.habit_combo.get()), None)
        if not selected_habit:
            messagebox.showerror("Error", "Please select a habit first!")
            return
        day_text = self.calendar_buttons[button_index]['text']
        if not day_text:
            return
        day = int(day_text)
        date = self.current_month.replace(day=day)
        color = self.calendar_buttons[button_index]['bg']
        if color == "white":
            self.db_manager.log_habit(selected_habit.id, date, True)
            self.current_habit_logs[date] = True
            self.calendar_buttons[button_index]['bg'] = "green"
        elif color == "green":
            self.db_manager.log_habit(selected_habit.id, date, False)
            self.current_habit_logs[date] = False
            self.calendar_buttons[button_index]['bg'] = "red"
        elif color == "red":
            self.db_manager.delete_habit_log(selected_habit.id, date)
            del self.current_habit_logs[date]
            self.calendar_buttons[button_index]['bg'] = "white"
        self.update_streak()

    def create_new_habit(self):
        habit_name = simpledialog.askstring("New Habit", "Enter habit name:")
        if habit_name:
            habit_id = self.db_manager.add_habit_for_user(habit_name, self.user.id)
            if habit_id:
                messagebox.showinfo("Habit Created", "Habit created successfully!")
                self.load_habits()
            else:
                messagebox.showerror("Error", "Error creating habit!")

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()

    def change_month(self, offset):
        if offset < 0:
            self.current_month = self.current_month.replace(day=1) - timedelta(days=1)
        else:
            self.current_month = self.current_month.replace(day=28) + timedelta(days=4)
        self.current_month = self.current_month.replace(day=1)
        self.update_calendar()

    def update_streak(self):
        streak = 0
        today = date.today()
        today_status = self.current_habit_logs.get(today)
        if today_status is None or not today_status:
            self.streak_label['text'] = "Current Streak: 0 days"
            return
        check_date = today
        while check_date in self.current_habit_logs and self.current_habit_logs[check_date]:
            streak += 1
            check_date -= timedelta(days=1)
        self.streak_label['text'] = f"Current Streak: {streak} days"

    def export_report(self):
        selected_habit = next((habit for habit in self.habits if habit.name == self.habit_combo.get()), None)
        if not selected_habit:
            messagebox.showerror("Error", "Please select a habit first!")
            return
        threading.Thread(target=self.export_report_thread, args=(selected_habit,)).start()

    def export_report_thread(self, habit):
        try:
            with open("habit_report.txt", "w") as f:
                f.write(habit.name + "\n")
                for date, status in self.current_habit_logs.items():
                    f.write(f"{date}: {status}\n")
            messagebox.showinfo("Export Success", "Report exported successfully to habit_report.txt!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report: {e}")

if __name__ == "__main__":
    # assuming you have a User class and a DatabaseManager class
    user = User("John Doe", "johndoe")
    db_manager = DatabaseManager()
    app = HabitTrackerApp(user, db_manager)
    app.root.mainloop()