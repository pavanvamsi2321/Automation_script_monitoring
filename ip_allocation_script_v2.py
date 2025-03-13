#v2.0
import subprocess
import ipaddress
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command: List[str], is_formatted: bool = False) -> Optional[Any]:
    """
    Executes a shell command using subprocess and processes output.

    Args:
        command (List[str]): The command to execute.
        is_formatted (bool): Whether to parse output as JSON.

    Returns:
        Optional[Any]: Parsed JSON data or tabular list, or None if an error occurs.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        if is_formatted:
            return json.loads(output)
        
        lines = output.splitlines()
        if not lines:
            return []
        
        headers = lines[0].split()
        return [{headers[i]: col for i, col in enumerate(line.split())} for line in lines[1:]]
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\n{e.stderr}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return None

def calculate_metrics(subnet_stats: Dict[str, Any]) -> Tuple[List[int], float, float]:
    """
    Calculates statistics about IP allocation within a subnet.

    Args:
        subnet_stats (dict): Subnet utilization details.

    Returns:
        Tuple[List[int], float, float]: Free IPs, mean free IPs, and mean allocation ratio.
    """
    free_ips_list = []
    sum_of_free_ips = 0.0
    sum_allocation_ratio = 0.0
    allocation_ratios = []

    for subnet in subnet_stats.get("subnetRangeStats", []):
        try:
            subnet_prefix = subnet["subnetRangePrefix"]
            allocation_ratio = subnet["allocationRatio"]
            allocation_ratios.append(allocation_ratio)

            network = ipaddress.ip_network(subnet_prefix, strict=False)
            total_ips = network.num_addresses
            allocated_ips = int(total_ips * allocation_ratio)
            free_ips = total_ips - allocated_ips
            free_ips_list.append(free_ips)
            sum_of_free_ips += free_ips * allocation_ratio
            sum_allocation_ratio += allocation_ratio
        except KeyError as e:
            logging.warning(f"Missing key in subnet stats: {e}")

    mean_free_ips = sum_of_free_ips / sum_allocation_ratio if sum_allocation_ratio else 0
    mean_allocation_ratio = sum(allocation_ratios) / len(allocation_ratios) if allocation_ratios else 0
    return free_ips_list, mean_free_ips, mean_allocation_ratio

# Get project ID from environment variable or fallback
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "pavan-project-github")
get_instance_command = [
    "gcloud", "recommender", "insights", "list",
    "--project", PROJECT_ID,
    "--location=global",
    "--insight-type=google.networkanalyzer.vpcnetwork.ipAddressInsight"
]

# Fetch instance data
instance_data = run_command(get_instance_command) or []

# Extract relevant instance IDs
instance_ids = [
    inst["INSIGHT_ID"] for inst in instance_data
    if inst.get("INSIGHT_SUBTYPE", "").upper() == "IP_UTILIZATION_SUMMARY" and inst.get("INSIGHT_STATE", "").upper() == "ACTIVE"
]

response_dict = {}

def process_instance(instance_id: str):
    """Fetch and process IP utilization details for a given instance ID."""
    read_instance_data_command = [
        "gcloud", "recommender", "insights", "describe", instance_id,
        "--project", PROJECT_ID,
        "--location=global",
        "--insight-type=google.networkanalyzer.vpcnetwork.ipAddressInsight",
        "--format=json"
    ]
    response = run_command(read_instance_data_command, is_formatted=True)
    
    if response and "content" in response:
        try:
            network_stats = response["content"].get("ipUtilizationSummaryInfo", [])[0].get("networkStats", [])
            for record in network_stats:
                for subnet_stats in record.get("subnetStats", []):
                    free_ips_list, mean_free_ips, mean_allocation_ratio = calculate_metrics(subnet_stats)
                    resource = subnet_stats.get("subnetUri", "").split("/")[-1]
                    response_dict[resource] = {
                        "Mean_of_free_ips": mean_free_ips,
                        "Mean_of_allocation_ratio": mean_allocation_ratio
                    }
        except (IndexError, KeyError) as e:
            logging.warning(f"Unexpected response format for instance {instance_id}: {e}")

# Use ThreadPoolExecutor for parallel processing of instance IDs
with ThreadPoolExecutor() as executor:
    executor.map(process_instance, instance_ids)

logging.info(f"Final IP utilization summary: {json.dumps(response_dict, indent=2)}")