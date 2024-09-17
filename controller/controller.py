import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
import re

if __name__ == '__main__':
    # number of samples
    n_samples = 2500

    # Create x axis from 0 to 2500
    x_values = np.arange(0, n_samples)

    # Straight line going from a 0 to 100 with 2500 samples
    linear_component = np.linspace(0, 1000, n_samples)

    frequency = 15
    amplitude = 30
    sinusoidal_component = amplitude * np.sin(2 * np.pi * frequency * x_values / n_samples)

    # Combination of the two components
    y_values = linear_component + sinusoidal_component

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)
    plt.title("Curva di carico con trend crescente e oscillazioni")
    plt.xlabel("Campioni")
    plt.ylabel("Valori")
    plt.grid(True)
    plt.show()

    step_function = np.floor(y_values/100)


    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label='Curva originale')
    plt.step(x_values, step_function, label='Funzione a gradino', color='red')

    # Aggiungere titolo e legenda
    plt.title("Curva originale e quantizzata a gradino")
    plt.xlabel("Campioni")
    plt.ylabel("Valori")
    plt.grid(True)
    plt.legend()

    # Mostriamo il grafico
    plt.show()

    plt.plot(x_values, step_function)
    plt.title("Curva quantizzata a gradino")
    plt.xlabel("Campioni")
    plt.ylabel("Valori")
    plt.grid(True)
    plt.legend()
    plt.show()

    url = "http://localhost:8080/get_value_from_API"
    results_df = pd.DataFrame(columns=["inputLevel", "response"])
    application_name = "APP3"
    api_name="API1"

    data_list = []

    for i in range(len(step_function)):
        # Prepara i dati JSON da inviare al server
        data = {
            "application_name" : application_name,
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

        # time.sleep(0.1)

    results_df = pd.DataFrame(data_list)
    print(results_df)