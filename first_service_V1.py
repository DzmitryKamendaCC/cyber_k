import configparser
import json
import random
import time
import requests


config_file = 'config.ini'

def send_event(endpoint, event):
    """Siunčia įvykį į serverį.

    Args:
        endpoint: Adresas, kur siųsti įvykį.
        event: Įvykio duomenys.

    Siunčia įvykį į nurodytą adresą ir 
    patikrina, ar serveris grąžino sėkmės kodą.
    Jei ne, išmeta klaidą.
    """
    try:
        # Siunčia POST užklausą su įvykio duomenimis
        response = requests.post(endpoint, json=event)
        # Patikrina, ar serveris grąžino sėkmės kodą (200)
        # response.raise_for_status()
        print(f"Įvykis išsiųstas: {event}")
    # Jei įvyko klaida, atspausdina klaidą
    except requests.exceptions.RequestException as e:
        print(f"Klaida siunčiant įvykį: {e}")



def read_config(config_path=config_file):
    """Nuskaito konfigūracijos failą.

    Args:
        config_path: Konfigūracijos failo kelias.

    Returns:
        Tuple su konfigūracijos reikšmėmis

    Nuskaito reikšmes iš konfigūracijos failo.
    Jei failo nėra arba jame yra klaidų, grąžinamos numatytosios reikšmės (fallback).
    """
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        logic_value = config.getint('while', 'logic')
        period_value = config.getint('first_service', 'period')
        endpoint_value = config.get('first_service', 'endpoint')
        events_file_value = config.get('first_service', 'events_file')
        return logic_value, period_value, endpoint_value, events_file_value
    except configparser.Error as e:
        print(f"Klaida skaitant konfigūracijos failą: {e}")
        return 1, 5, "http://localhost:8000/event", "events.json"  



def main():
    """
    Nuskaito konfigūracijos parametrus, periodiškai siunčia 
    atsitiktinius įvykius į nurodytą endpoint'ą ir tikrina, 
    ar tęsti ciklą pagal konfigūracijos failo nustatymus.
    """

    run_task = True
    while run_task:
        # Nuskaitomos konfigūracijos reikšmės
        logic, period, endpoint, events_file = read_config()

        with open(events_file, "r") as f:
            events = json.load(f)
        # Pasirenkamas atsitiktinis įvykis
        event = random.choice(events)
        # Siunčiamas įvykis
        send_event(endpoint, event)
        print("issiunte")
        # Laukiama nurodytą laiką
        time.sleep(period)

        # Pasitikrinam ar norim vis dar tęsti siuntimą, jei ne, tai konfiguraciniam pakeičiam
        # while sekcijos logic kintamajį į bet kokį kitą skaičiu tik ne 1 ir while ciklas nutrūksta
        if logic != 1:
            run_task = False

if __name__ == "__main__":
    main()