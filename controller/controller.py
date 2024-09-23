import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import re
import time


def reset_conf(component_name):
    reset_data = {
        "component_name": component_name,
        "confHW": 0
    }
    try:
        reset_response = requests.post("http://localhost:8080/set_confHW", json=reset_data)
        if reset_response.status_code == 200:
            return True
        else:
            print(f"Error in the request: {reset_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    return False


def set_new_confhw(component):
    new_confURL = "http://localhost:8080/set_confHW"
    data = {
        "component_name": component
    }
    try:
        response = requests.post(new_confURL, json=data)
        if response.status_code == 200:
            result = response.text
            match = re.search(r"Current HW configuration: ([\d.]+)", result)
            if match:
                currentHW = int(match.group(1))
                currentHW += 1
                new_data = {
                    "component_name": component,
                    "confHW": currentHW
                }
                response = requests.post(new_confURL, json=new_data)
                if response.status_code == 200:
                    return currentHW
            else:
                print(f"Pattern not found: {result}")
        else:
            print(f"Error in the request: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    return False


def create_load_curve(n_samples, frequency, amplitude):
    # Create x-axis from 0 to n_samples
    x = np.arange(0, n_samples)
    # Straight line going from a 0 to 1000 with n_samples samples
    linear_component = np.linspace(0, 1000, n_samples)

    sinusoidal_component = amplitude * np.sin(2 * np.pi * frequency * x / n_samples)

    # Combination of the two components
    y = linear_component + sinusoidal_component
    return x, y


if __name__ == '__main__':
    x_values, y_values = create_load_curve(2500, 15, 30)
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)
    plt.title("Load curve with increasing trend and oscillations")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.show()

    step_function = np.floor(y_values / 100)

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label='Original curve')
    plt.step(x_values, step_function, label='Step function', color='red')

    plt.title("Original curve and step function")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.plot(x_values, step_function, label="Step Function")
    plt.title("Step function")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.show()

    url = "http://localhost:8080/get_value_from_API"
    results_df = pd.DataFrame(columns=["inputLevel", "response"])
    application_name = "APP3"
    api_name = "API0"

    data_list = []
    SLO = 20
    component_name = "component1"
    for i in range(len(step_function)):
        # Prepares JSON data to be sent to the server
        data = {
            "application_name": application_name,
            "api_name": api_name,
            "inputLevel": int(step_function[i])
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.text
                match = re.search(r"Value ([\d.]+) ms", result)
                if match:
                    time_ms = match.group(1)
                    data_list.append({
                        "inputLevel": data["inputLevel"],
                        "response": float(time_ms)
                    })
                else:
                    print(f"Pattern not found: {result}")
            else:
                print(f"Error in the request for inputLevel {data['inputLevel']}: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")

    results_df = pd.DataFrame(data_list)
    print(results_df)
    results_df.to_csv('output.csv')

    plt.figure(figsize=(10, 6))
    plt.plot(results_df['inputLevel'], results_df['response'])
    plt.xlabel('Input Level')
    plt.ylabel('Response')
    plt.title('Graph between Input Level and Response without control')
    plt.grid(True)
    plt.show()

    start_time = pd.Timestamp('2023-09-17 00:00:00')
    timestamps = pd.date_range(start=start_time, periods=len(results_df), freq='min')
    results_df['SLO'] = SLO
    results_df['timestamp'] = timestamps
    results_df.to_csv('output_with_timestamp_and_SLO.csv', index=False)

    plt.plot(results_df['timestamp'], results_df['response'], label='confHW0')
    plt.axhline(y=SLO, color='red', linestyle='--', label='SLO')
    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.ylabel('Response time (ms)')
    plt.title('Graph between timestamps and response time without control')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Control

    control_data_list = []
    for i in range(len(step_function)):
        # Prepares JSON data to be sent to the server
        data = {
            "application_name": application_name,
            "api_name": api_name,
            "inputLevel": int(step_function[i])
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.text
                match = re.search(r"Value ([\d.]+) ms", result)
                if match:
                    time_ms = match.group(1)
                    control_data_list.append({
                        "inputLevel": data["inputLevel"],
                        "response": float(time_ms)
                    })
                    if float(time_ms) > SLO:
                        result = set_new_confhw(component_name)
                        if result > 0:
                            print(f"New Configuration setted: {result}")
                else:
                    print(f"Pattern not found: {result}")
            else:
                print(f"Error in the request for inputLevel {data['inputLevel']}: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")

    control_results_df = pd.DataFrame(control_data_list)
    print(control_results_df)
    control_results_df.to_csv('Control_output.csv')

    start_time = pd.Timestamp('2023-09-17 00:00:00')
    timestamps = pd.date_range(start=start_time, periods=len(control_results_df), freq='min')
    control_results_df['SLO'] = SLO
    control_results_df['timestamp'] = timestamps
    control_results_df.to_csv('Control_output_with_timestamp_and_SLO.csv', index=False)

    plt.plot(control_results_df['timestamp'], control_results_df['response'])
    plt.axhline(y=SLO, color='red', linestyle='--', label='SLO')
    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.ylabel('Response time (ms)')
    plt.title('Graph between timestamps and response time with control')
    plt.grid(True)
    plt.legend()
    plt.show()

    reset_conf("component1")
