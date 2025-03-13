# UTILIZATION OF IP ALLOCATION SUMMARY
import subprocess
import ipaddress
import json

def run_command(command, is_formatted=False):
    """
    Executes a shell command using subprocess, captures the output, 
    and processes it either as a JSON response or as tabular data.

    Args:
        command (list): List of command arguments to execute.
        is_formatted (bool): Flag to determine if the output should be parsed as JSON.

    Returns:
        list or dict: Parsed output data, either in JSON format or as a list of dictionaries.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)

        # If JSON format is expected, parse the response
        if is_formatted:
            json_response_data = json.loads(result.stdout)
            print(json_response_data)
            return json_response_data

        # Process standard command output as tabular data
        lines = result.stdout.strip().splitlines()
        headers = lines[0].split()
        data = []
        for line in lines[1:]:
            columns = line.split()
            row_dict = {headers[i]: columns[i] for i in range(len(headers))}
            data.append(row_dict)

        print(data)
        return data

    except subprocess.CalledProcessError as e:
        print("Error occurred while executing the command:")
        print(e.stderr)
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:")
        print(e)


def calculate_metrics(subnet_stats):
    """
    Calculates and prints statistics about IP allocation within a subnet.

    Args:
        subnet_stats (dict): Dictionary containing details about subnet utilization.

    Returns:
        tuple: (list of free IPs, mean free IPs, mean allocation ratio)
    """
    free_ips_list = []
    sum_of_free_ips = 0
    sum_allocation_ratio = 0
    allocation_ratios = []

    # Iterate through subnet statistics
    for subnet in subnet_stats.get("subnetRangeStats", []):
        subnet_prefix = subnet["subnetRangePrefix"]
        allocation_ratio = subnet["allocationRatio"]
        allocation_ratios.append(allocation_ratio)

        # Calculate total IPs in the subnet
        network = ipaddress.ip_network(subnet_prefix, strict=False)
        total_ips = network.num_addresses

        # Compute free IPs based on allocation ratio
        allocated_ips = int(total_ips * allocation_ratio)
        free_ips = total_ips - allocated_ips
        free_ips_list.append(free_ips)

        # Weighted sum calculation
        sum_of_free_ips += free_ips * allocation_ratio
        sum_allocation_ratio += allocation_ratio

        print(f"Subnet: {subnet_prefix}, Total IPs: {total_ips}, Allocated: {allocated_ips}, Free: {free_ips}")

    # Calculate mean values with proper checks
    mean_free_ips = sum_of_free_ips / sum_allocation_ratio if sum_allocation_ratio else 0
    mean_allocation_ratio = sum(allocation_ratios) / len(allocation_ratios) if allocation_ratios else 0

    print(f"\nMean Free IPs (Weighted by Allocation Ratio): {mean_free_ips}")
    print(f"Mean Allocation Ratio: {mean_allocation_ratio}")

    return free_ips_list, mean_free_ips, mean_allocation_ratio


# Command to list IP utilization insights from Google Cloud
get_instance_command = [
    "gcloud", "recommender", "insights", "list",
    "--project=pavan-project-github",
    "--location=global",
    "--insight-type=google.networkanalyzer.vpcnetwork.ipAddressInsight"
]

# Fetch instance data
instance_data = run_command(get_instance_command)
instance_ids = []

# Filter instances that match the required conditions
for instance in instance_data:
    if instance.get("INSIGHT_SUBTYPE", "").upper() == "IP_UTILIZATION_SUMMARY" and instance.get("INSIGHT_STATE", "").upper() == "ACTIVE":
        instance_ids.append(instance.get("INSIGHT_ID"))

print(instance_ids)
response_dict = {}

# Iterate through filtered instance IDs to gather detailed IP utilization insights
for instance_id in instance_ids:
    read_instance_data_command = [
        "gcloud", "recommender", "insights", "describe", instance_id,
        "--project=pavan-project-github",
        "--location=global",
        "--insight-type=google.networkanalyzer.vpcnetwork.ipAddressInsight",
        "--format=json"
    ]
    
    response = run_command(read_instance_data_command, is_formatted=True)

    # Extract relevant network stats
    filtered_response = response["content"]["ipUtilizationSummaryInfo"][0]["networkStats"]
    for record in filtered_response:
        print(record)

        # Process subnet statistics for each network
        for subnet_stats in record.get("subnetStats", []):
            free_ips_list, mean_free_ips, mean_allocation_ratio = calculate_metrics(subnet_stats)

            # Extract subnet name and store results in dictionary
            resource = subnet_stats.get("subnetUri", "").split("/")[-1]
            response_dict[resource] = {"Mean_of_free_ips": mean_free_ips, "Mean_of_allocation_ratio": mean_allocation_ratio}

print(response_dict)
