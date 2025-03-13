Here’s a reformatted version of the `README.md` for better clarity and structure:

```markdown
# Automation Script Monitoring

This repository contains Python scripts for analyzing IP allocation and utilization in a Google Cloud Platform (GCP) project.

## IP Allocation Script

### Overview

This folder contains Python scripts (v1.0 and v2.0) to analyze IP allocation statistics in a Google Cloud Platform (GCP) project using the `gcloud` command-line tool. The script automates the process of collecting, analyzing, and summarizing IP address utilization insights after enabling the Recommender API for the project ID. The goal of this script is to obtain a detailed understanding of IP address allocation in different subnets within a specified project and region, calculate free IP metrics, and provide a high-level summary of the IP allocation.

I developed this script to address a challenge in a previous project. The script performs the following key tasks:

- Fetches insights on IP utilization.
- Processes and filters the data.
- Calculates key metrics such as free IPs, allocation ratio, and provides an aggregated result.

### Features

#### v1.0
- Fetches IP utilization insights using `gcloud` commands.
- Parses JSON responses and tabular data.
- Computes metrics such as mean free IPs and allocation ratio.

#### v2.0 (Enhanced)
- Implements structured logging for better debugging.
- Uses `ThreadPoolExecutor` for concurrent processing.
- Enhances error handling with proper exception management.
- Supports project configuration via environment variables.

## Prerequisites

Ensure the following dependencies are installed:

- Python 3.x
- Google Cloud SDK (gcloud CLI)
- Required Python modules:
  - `subprocess`
  - `ipaddress`
  - `json`
  - `logging`
  - `concurrent.futures`
  - `os`

## Setup & Usage

### Step 1: Set Up GCP Authentication

Authenticate using `gcloud` and set up your project:

```bash
# Authenticate
gcloud auth login

# Set the active project
export GCP_PROJECT_ID="your-project-id"
```

### Step 2: Run the Script

Run `v1.0`:

```bash
python3 ip_allocation_script.py
```

Run `v2.0`:

```bash
python3 ip_allocation_script_v2.py
```

### Step 3: View Output

The script outputs IP utilization insights and subnet statistics, such as:

- Mean free IPs
- Mean allocation ratio
- Subnet allocation details

## Contribution

Feel free to fork this repository and submit pull requests for improvements!
```
