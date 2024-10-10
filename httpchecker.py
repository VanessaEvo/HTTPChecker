import pyfiglet
import requests
from tqdm import tqdm

def check_domain(domain):
    try:
        response = requests.get(f"https://{domain}", stream=True)
        status_code = response.status_code
        headers = response.headers
        redirect_history = response.history
        return status_code, headers, redirect_history
    except requests.exceptions.RequestException as e:
        return None, None, None

ascii_banner = pyfiglet.figlet_format("HTTP Checker")
print(ascii_banner)
print("https://github.com/VanessaEvo")
print("========================================================")

# Prompt the user for the path of the domain list file
domain_list_path = input("Enter the path and name of the domain list file: ")

# Read domains from the specified file
with open(domain_list_path, 'r') as file:
    domains = file.read().splitlines()

# Prompt the user for the path to save the results
results_path = input("Enter the path and name of file to save the results: ")

# Open the file to save the results
with open(results_path, 'w') as results_file:
    for domain in domains:
        status_code, headers, redirect_history = check_domain(domain)
        results_file.write(f"Domain: {domain}\n")
        results_file.write(f"Status Code: {status_code}\n")
        results_file.write(f"Headers: {headers}\n")
        results_file.write(f"Redirect History: {redirect_history}\n")
        results_file.write("------------------------\n")
        print(f"Domain: {domain} - Status Code: {status_code}")

print("Scan completed. Results saved to:", results_path)