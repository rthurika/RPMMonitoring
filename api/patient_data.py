"""
API client for the Remote Patient Monitoring application
"""

import requests
from config import BASE_URL


def fetch_patient_data(patient_id):
    """
    Fetch patient data from the API
    """
    response = requests.get(BASE_URL.format(patient_id))
    response.raise_for_status()
    return response.json()


def send_patient_message(patient_id, message):
    """
    Send a message to a patient
    """
    payload = {"message": message}
    response = requests.post(
        BASE_URL.format(patient_id),
        json=payload
    )
    response.raise_for_status()
    return response.json()