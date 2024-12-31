
from scipy.stats import poisson
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import threading
import queue
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Patient:
    def __init__(self, id: int, arrival_time: datetime, priority: int = 1):
        self.id = id
        self.arrival_time = arrival_time
        self.service_start_time: Optional[datetime] = None
        self.service_end_time: Optional[datetime] = None
        self.priority = priority  # 1 = normal, 2 = urgent, 3 = emergency
        self.service_duration: Optional[int] = None


class InteractiveHospitalQueue:
    def __init__(self, avg_service_rate: float = 4):
        self.avg_service_rate = avg_service_rate
        self.queue = queue.PriorityQueue()
        self.current_patient: Optional[Patient] = None
        self.completed_patients: List[Patient] = []
        self.patient_counter = 0
        self.is_running = False
        self.service_thread = None
        self.update_thread = None

        # Create main window
        self.root = tk.Tk()
        self.root.title("Interactive Hospital Queue Simulation")
        self.setup_gui()

    def setup_gui(self):
        # Create frames
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        stats_frame = ttk.Frame(self.root, padding="10")
        stats_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        queue_frame = ttk.Frame(self.root, padding="10")
        queue_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Control buttons
        ttk.Button(control_frame, text="Add Normal Patient",
                   command=lambda: self.add_patient(1)).grid(row=0, column=0, pady=5)
        ttk.Button(control_frame, text="Add Urgent Patient",
                   command=lambda: self.add_patient(2)).grid(row=1, column=0, pady=5)
        ttk.Button(control_frame, text="Add Emergency Patient",
                   command=lambda: self.add_patient(3)).grid(row=2, column=0, pady=5)

        self.start_stop_button = ttk.Button(control_frame, text="Start Service",
                                            command=self.toggle_service)
        self.start_stop_button.grid(row=3, column=0, pady=5)

        # Statistics labels
        self.stats_labels = {}
        stats = ["Patients in Queue:", "Current Patient:", "Average Wait Time:",
                 "Max Wait Time:", "Completed Patients:"]
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text=stat).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0")
            self.stats_labels[stat].grid(row=i, column=1, sticky=tk.W, pady=2)

        # Queue display
        self.queue_tree = ttk.Treeview(queue_frame, columns=("ID", "Wait Time", "Priority"),
                                       show="headings")
        self.queue_tree.heading("ID", text="Patient ID")
        self.queue_tree.heading("Wait Time", text="Wait Time (min)")
        self.queue_tree.heading("Priority", text="Priority")
        self.queue_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for queue display
        scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_tree.configure(yscrollcommand=scrollbar.set)

        # Setup plotting
        self.fig = Figure(figsize=(8, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def add_patient(self, priority: int):
        self.patient_counter += 1
        patient = Patient(
            id=self.patient_counter,
            arrival_time=datetime.now(),
            priority=priority
        )
        # Priority queue uses tuples of (priority, arrival_time, patient)
        # Negating priority ensures higher priority (3) comes before lower priority (1)
        self.queue.put((-priority, patient.arrival_time.timestamp(), patient))
        self.update_display()

    def toggle_service(self):
        if not self.is_running:
            self.is_running = True
            self.start_stop_button.configure(text="Stop Service")
            self.service_thread = threading.Thread(target=self.run_service)
            self.update_thread = threading.Thread(target=self.update_display_loop)
            self.service_thread.daemon = True
            self.update_thread.daemon = True
            self.service_thread.start()
            self.update_thread.start()
        else:
            self.is_running = False
            self.start_stop_button.configure(text="Start Service")

    def run_service(self):
        while self.is_running:
            if self.current_patient is None and not self.queue.empty():
                _, _, patient = self.queue.get()
                self.current_patient = patient
                self.current_patient.service_start_time = datetime.now()
                self.current_patient.service_duration = int(poisson.rvs(mu=60 / self.avg_service_rate))
                time.sleep(self.current_patient.service_duration)
                self.current_patient.service_end_time = datetime.now()
                self.completed_patients.append(self.current_patient)
                self.current_patient = None
            time.sleep(0.1)

    def update_display_loop(self):
        while self.is_running:
            self.update_display()
            time.sleep(1)

    def update_display(self):
        # Clear queue display
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)

        # Add current queue items
        temp_queue = queue.PriorityQueue()
        while not self.queue.empty():
            priority, timestamp, patient = self.queue.get()
            wait_time = (datetime.now() - patient.arrival_time).total_seconds() / 60
            self.queue_tree.insert("", tk.END, values=(
                f"Patient {patient.id}",
                f"{wait_time:.1f}",
                "Emergency" if patient.priority == 3 else
                "Urgent" if patient.priority == 2 else "Normal"
            ))
            temp_queue.put((priority, timestamp, patient))

        # Restore queue
        while not temp_queue.empty():
            self.queue.put(temp_queue.get())

        # Update statistics
        self.stats_labels["Patients in Queue:"].configure(
            text=str(self.queue.qsize()))
        self.stats_labels["Current Patient:"].configure(
            text=f"Patient {self.current_patient.id}" if self.current_patient else "None")

        if self.completed_patients:
            wait_times = [(p.service_start_time - p.arrival_time).total_seconds() / 60
                          for p in self.completed_patients]
            avg_wait = sum(wait_times) / len(wait_times)
            max_wait = max(wait_times)
            self.stats_labels["Average Wait Time:"].configure(text=f"{avg_wait:.1f} min")
            self.stats_labels["Max Wait Time:"].configure(text=f"{max_wait:.1f} min")

        self.stats_labels["Completed Patients:"].configure(
            text=str(len(self.completed_patients)))

        # Update plot
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        if self.completed_patients:
            wait_times = [(p.service_start_time - p.arrival_time).total_seconds() / 60
                          for p in self.completed_patients]
            self.ax.hist(wait_times, bins=20, alpha=0.75)
            self.ax.set_xlabel("Waiting Time (minutes)")
            self.ax.set_ylabel("Number of Patients")
            self.ax.set_title("Distribution of Waiting Times")
            self.canvas.draw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    simulation = InteractiveHospitalQueue(avg_service_rate=4)
    simulation.run()