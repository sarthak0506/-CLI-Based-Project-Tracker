import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime

projects = {}


def add_project():
    name = project_name_var.get().strip()
    rate = hourly_rate_var.get().strip()

    if name == "" or rate == "":
        messagebox.showerror("Input Error", "Project name and hourly rate are required.")
        return

    try:
        rate = float(rate)
    except ValueError:
        messagebox.showerror("Input Error", "Hourly rate must be a number.")
        return

    if name in projects:
        messagebox.showwarning("Exists", "Project already exists.")
        return

    projects[name] = {"rate": rate, "logs": []}
    messagebox.showinfo("Success", f"Project '{name}' added.")
    update_project_dropdown()


def update_project_dropdown():
    project_dropdown['menu'].delete(0, 'end')
    for project in projects:
        project_dropdown['menu'].add_command(label=project, command=tk._setit(selected_project, project))
    selected_project.set("Select Project")


def log_time():
    project = selected_project.get()
    start = start_time_var.get().strip()
    end = end_time_var.get().strip()
    note = note_var.get().strip()

    if project not in projects:
        messagebox.showerror("Error", "Project not found.")
        return

    try:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        duration = (end_dt - start_dt).seconds / 3600
        if duration <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Time", "Start and end time must be in HH:MM format and end must be after start.")
        return

    projects[project]["logs"].append({
        "start": start,
        "end": end,
        "duration": duration,
        "note": note
    })

    messagebox.showinfo("Success", f"{duration:.2f} hours logged for '{project}'.")
    refresh_table()
    show_summary()


def refresh_table():
    for row in log_table.get_children():
        log_table.delete(row)
    for project, data in projects.items():
        for log in data["logs"]:
            bill = log["duration"] * data["rate"]
            log_table.insert("", "end", values=(
            project, log["start"], log["end"], f"{log['duration']:.2f}", log["note"], data["rate"], f"{bill:.2f}"))


def show_summary():
    summary_box.delete("1.0", tk.END)
    for project, data in projects.items():
        total_time = sum(log["duration"] for log in data["logs"])
        total_bill = total_time * data["rate"]
        summary_box.insert(tk.END, f"{project}: {total_time:.2f} hrs → ₹{total_bill:.2f}\n")


def export_csv():
    with open("project_logs_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Project", "Start", "End", "Duration (hrs)", "Note", "Hourly Rate", "Bill (₹)"])
        for project, data in projects.items():
            for log in data["logs"]:
                bill = log["duration"] * data["rate"]
                writer.writerow([project, log["start"], log["end"], f"{log['duration']:.2f}", log["note"], data["rate"],
                                 f"{bill:.2f}"])
    messagebox.showinfo("Exported", "Project logs exported to 'project_logs_export.csv'")

 #GUI

root = tk.Tk()
root.title("🛠️ Project Tracker - GUI")

# --- Add Project Section ---
tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(root, text="Hourly Rate (₹):").grid(row=0, column=2, padx=5, pady=5)

project_name_var = tk.StringVar()
hourly_rate_var = tk.StringVar()

tk.Entry(root, textvariable=project_name_var).grid(row=0, column=1)
tk.Entry(root, textvariable=hourly_rate_var).grid(row=0, column=3)

tk.Button(root, text="➕ Add Project", command=add_project).grid(row=0, column=4, padx=10)

# --- Log Time Section ---
tk.Label(root, text="Select Project:").grid(row=1, column=0)
tk.Label(root, text="Start (HH:MM):").grid(row=1, column=1)
tk.Label(root, text="End (HH:MM):").grid(row=1, column=2)
tk.Label(root, text="Note:").grid(row=1, column=3)

selected_project = tk.StringVar(value="Select Project")
project_dropdown = tk.OptionMenu(root, selected_project, "Select Project")
project_dropdown.grid(row=2, column=0)

start_time_var = tk.StringVar()
end_time_var = tk.StringVar()
note_var = tk.StringVar()

tk.Entry(root, textvariable=start_time_var).grid(row=2, column=1)
tk.Entry(root, textvariable=end_time_var).grid(row=2, column=2)
tk.Entry(root, textvariable=note_var).grid(row=2, column=3)

tk.Button(root, text="🕒 Log Time", command=log_time).grid(row=2, column=4, padx=10)


cols = ["Project", "Start", "End", "Duration (hrs)", "Note", "Hourly Rate", "Bill (₹)"]
log_table = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    log_table.heading(col, text=col)
log_table.grid(row=3, column=0, columnspan=5, padx=10, pady=10)


tk.Button(root, text="📤 Export to CSV", command=export_csv).grid(row=4, column=0, padx=10)
summary_box = tk.Text(root, height=5, width=60)
summary_box.grid(row=4, column=1, columnspan=4, padx=10, pady=10)


root.mainloop()
