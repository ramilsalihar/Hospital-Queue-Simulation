# hospital_queue_simulation.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson
from datetime import datetime, timedelta


class HospitalQueueSimulation:
    def __init__(self, avg_arrival_rate, avg_service_rate, num_hours=8):
        """
        Initialize simulation parameters

        Args:
            avg_arrival_rate: Average number of patients arriving per hour
            avg_service_rate: Average number of patients that can be served per hour
            num_hours: Number of hours to simulate
        """
        self.avg_arrival_rate = avg_arrival_rate
        self.avg_service_rate = avg_service_rate
        self.num_hours = num_hours

    def generate_arrivals(self):
        """Generate random patient arrivals using Poisson distribution"""
        arrivals = poisson.rvs(mu=self.avg_arrival_rate, size=self.num_hours)
        return arrivals

    def generate_service_times(self, total_patients):
        """Generate random service times using Poisson distribution"""
        service_times = poisson.rvs(mu=60 / self.avg_service_rate, size=total_patients)
        return service_times  # in minutes

    def run_simulation(self):
        """Run the queue simulation"""
        # Generate arrivals for each hour
        hourly_arrivals = self.generate_arrivals()
        total_patients = sum(hourly_arrivals)

        # Generate arrival times throughout the day
        arrival_times = []
        current_time = datetime.strptime('08:00', '%H:%M')  # Start at 8 AM

        for hour, num_arrivals in enumerate(hourly_arrivals):
            if num_arrivals > 0:
                # Distribute arrivals randomly within the hour
                minute_offsets = np.random.uniform(0, 60, num_arrivals)
                for offset in minute_offsets:
                    arrival_time = current_time + timedelta(hours=hour, minutes=offset)
                    arrival_times.append(arrival_time)

        # Sort arrival times
        arrival_times.sort()

        # Generate service times
        service_times = self.generate_service_times(total_patients)

        # Calculate waiting times and queue lengths
        waiting_times = []
        queue_lengths = []
        service_start_times = []
        current_queue = 0
        last_service_end = arrival_times[0]

        for i in range(len(arrival_times)):
            arrival = arrival_times[i]
            service_time = service_times[i]

            # Update service start time
            service_start = max(arrival, last_service_end)
            service_start_times.append(service_start)

            # Calculate waiting time
            waiting_time = (service_start - arrival).total_seconds() / 60  # in minutes
            waiting_times.append(waiting_time)

            # Update last service end time
            last_service_end = service_start + timedelta(minutes=service_time)

            # Update queue length
            current_queue = sum(1 for j in range(i + 1, len(arrival_times))
                                if arrival_times[j] <= service_start)
            queue_lengths.append(current_queue)

        # Create DataFrame with results
        self.results = pd.DataFrame({
            'arrival_time': arrival_times,
            'service_start': service_start_times,
            'service_duration': service_times,
            'waiting_time': waiting_times,
            'queue_length': queue_lengths
        })

        return self.results

    def plot_results(self):
        """Create visualizations of the simulation results"""
        if not hasattr(self, 'results'):
            raise ValueError("Run simulation first using run_simulation()")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Hospital Queue Simulation Results', fontsize=16)

        # 1. Waiting Time Distribution
        sns.histplot(data=self.results, x='waiting_time', bins=20, ax=axes[0, 0])
        axes[0, 0].set_title('Distribution of Waiting Times')
        axes[0, 0].set_xlabel('Waiting Time (minutes)')
        axes[0, 0].set_ylabel('Count')

        # 2. Queue Length Over Time
        axes[0, 1].plot(self.results['arrival_time'], self.results['queue_length'])
        axes[0, 1].set_title('Queue Length Over Time')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Number of Patients in Queue')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Service Time Distribution
        sns.histplot(data=self.results, x='service_duration', bins=20, ax=axes[1, 0])
        axes[1, 0].set_title('Distribution of Service Times')
        axes[1, 0].set_xlabel('Service Time (minutes)')
        axes[1, 0].set_ylabel('Count')

        # 4. Average Waiting Time by Hour
        self.results['hour'] = self.results['arrival_time'].dt.hour
        hourly_avg_wait = self.results.groupby('hour')['waiting_time'].mean()
        hourly_avg_wait.plot(kind='bar', ax=axes[1, 1])
        axes[1, 1].set_title('Average Waiting Time by Hour')
        axes[1, 1].set_xlabel('Hour of Day')
        axes[1, 1].set_ylabel('Average Waiting Time (minutes)')

        plt.tight_layout()
        plt.show()

    def get_statistics(self):
        """Calculate and return summary statistics"""
        if not hasattr(self, 'results'):
            raise ValueError("Run simulation first using run_simulation()")

        stats = {
            'average_waiting_time': self.results['waiting_time'].mean(),
            'max_waiting_time': self.results['waiting_time'].max(),
            'average_queue_length': self.results['queue_length'].mean(),
            'max_queue_length': self.results['queue_length'].max(),
            'total_patients': len(self.results),
            'average_service_time': self.results['service_duration'].mean()
        }

        return stats


# Example usage
if __name__ == "__main__":
    # Initialize simulation with parameters
    simulation = HospitalQueueSimulation(
        avg_arrival_rate=5,  # Average 5 patients arriving per hour
        avg_service_rate=4,  # Can serve 4 patients per hour on average
        num_hours=8  # 8-hour simulation
    )

    # Run simulation
    results = simulation.run_simulation()

    # Plot results
    simulation.plot_results()

    # Get and print statistics
    stats = simulation.get_statistics()
    print("\nSimulation Statistics:")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value:.2f}")