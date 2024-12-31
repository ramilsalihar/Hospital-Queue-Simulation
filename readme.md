# Hospital Queue Simulation Using Poisson Distribution

## Overview
Python-based simulation of hospital queues using Poisson distribution to model patient arrivals and service times. This tool helps predict waiting times and queue lengths in a hospital setting.

## Technical Requirements
- Python 3.8 or higher
- Memory: Minimum 4GB RAM
- Storage: 100MB free space
- Operating System: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

## Dependencies
```
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
python-dateutil>=2.8.2
```

## Quick Start
1. Clone the repository:
```bash
git clone https://github.com/yourusername/hospital-queue-simulation.git
cd hospital-queue-simulation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulation:

## Theory Summary
The simulation uses Poisson distribution to model:
- Patient arrivals: Random arrivals with known average rate
- Service times: Variable treatment durations
- Queue dynamics: Waiting times and queue length calculations

## Key Features
- Simulates patient arrivals and service times
- Calculates waiting times and queue lengths
- Generates visualizations:
  - Waiting time distribution
  - Queue length over time
  - Service time distribution
  - Hourly average waiting times
- Provides summary statistics

## Limitations
- Single queue model only
- Constant arrival rates within each hour
- No priority queue system
- Doesn't account for staff breaks

## Example Output
```python
# Returns:
# - Average waiting time
# - Maximum waiting time
# - Average queue length
# - Maximum queue length
# - Total patients served
# - Average service time
```

## License
MIT License