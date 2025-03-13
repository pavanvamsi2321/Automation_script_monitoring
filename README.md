# Automation_script_monitoring
This repository contains Python scripts for analyzing IP allocation and utilization in a Google Cloud Platform (GCP) project. 

IP Allocation Script
Overview
This folder contains Python scripts i.e., v1.0 and 2.0 to analyze the IP allocation statistics in a Google Cloud Platform (GCP) project using the gcloud command-line tool. This Python script automates the process of collecting, analyzing, and summarizing IP address utilization insights after enabling the recommender API for project ID. The script goal is to obtain a detailed understanding of IP address allocation in different subnets within a specified project and region, free IP metrics and provide a high-level summary of the IP allocation. I have prepared this script to handle one of the challenges in my previous project. 
The script performs the following key tasks:
•	Fetches insights on IP utilization.
•	Processes and filters the data.
•	Calculates key metrics such as free IPs, allocation ratio, and provides an aggregated result.
Features
v1.0
•	Fetches IP utilization insights using gcloud commands.
•	Parses JSON responses and tabular data.
•	Computes metrics such as mean free IPs and allocation ratio.
v2.0 (Enhanced)
•	Implements structured logging for better debugging.
•	Uses ThreadPoolExecutor for concurrent processing.
•	Enhances error handling with proper exception management.
•	Supports project configuration via environment variables.
Prerequisites
Please ensure the following dependencies are installed:
•	Python 3.x
•	Google Cloud SDK (gcloud CLI)
•	Required Python modules (subprocess, ipaddress, json, logging, concurrent.futures, os)
Setup & Usage
Step 1: Set Up GCP Authentication
Ensure you have authenticated using gcloud and set up your project:
# Authenticate
gcloud auth login
# Set the active project
export GCP_PROJECT_ID="your-project-id"
Step 2: Run the Script
Run v1.0
python3 ip_allocation_script.py
Run v2.0
python3 ip_allocation_script_v2.py
Step 3: View Output
The script outputs IP utilization insights and subnet statistics, such as:
•	Mean free IPs
•	Mean allocation ratio
•	Subnet allocation details
Contribution
Feel free to fork this repository and submit pull requests for improvements!
