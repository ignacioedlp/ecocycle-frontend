from flask import session
import requests
from decimal import Decimal
import os

# Base URL y credenciales
base_url = os.environ.get('BONITA_URL', 'http://localhost:8080/bonita')
username = os.environ.get('BONITA_USERNAME', 'walter.bates')
password = os.environ.get('BONITA_PASS', 'bpm')

# Funciones auxiliares
def authenticate():
    url = "/loginservice"
    payload = f'username={username}&password={password}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(base_url + url, data=payload, headers=headers)

    if response.status_code == 204:
        bonita_token = response.cookies.get('X-Bonita-API-Token')
        session_id = response.cookies.get('JSESSIONID')
        if bonita_token:
            print("Autenticación exitosa.")
            session['bonita_token'] = bonita_token  # Guardar en la sesión de Flask
            session['session_id'] = session_id  # Guardar en la sesión de Flask
            return bonita_token, session_id
        else:
            print("No se encontró el token X-Bonita-API-Token en la respuesta.")
            raise KeyError("No se encontró el token X-Bonita-API-Token en la respuesta.")
    else:
        print(f"Error de autenticación: {response.status_code}, {response.text}")
        raise Exception(f"Error de autenticación: {response.status_code}, {response.text}")

def get_process_id(process_name):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = "/API/bpm/process?s=" + process_name
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}'
    }

    response = requests.get(base_url + url, headers=headers)

    if response.content:
        return response.json()[0]['id'] if response.json() else None
    else:
        raise ValueError("Empty response received from the server")

def init_process(process_id):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = f"/API/bpm/process/{process_id}/instantiation"
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}'
    }

    response = requests.post(base_url + url, headers=headers)
    return response.json()['caseId'] if response.json() else None

def get_task_by_case(case_id):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = f"/API/bpm/task?f=caseId={case_id}"
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}'
    }

    response = requests.get(base_url + url, headers=headers)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if isinstance(json_data, list) and len(json_data) > 0:
                return json_data[0]['id']
            else:
                raise ValueError("La respuesta no contiene tareas asociadas al caseId.")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error al procesar la respuesta JSON: {e}")
    else:
        raise Exception(f"Error al obtener la tarea por caseId: {response.status_code}, {response.text}")

def assign_variable_by_task_and_case(case_id, variable_name, variable_value, variable_type):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = f"/API/bpm/caseVariable/{case_id}/{variable_name}"
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}',
        'Content-Type': 'application/json'
    }

    if isinstance(variable_value, Decimal):
        variable_value = str(variable_value)

    payload = {
        "type": variable_type,
        "value": variable_value
    }

    response = requests.put(base_url + url, headers=headers, json=payload)

    if response.status_code == 200 or response.status_code == 204:
        print(f"Variable {variable_name} asignada correctamente.")
    else:
        print(f"Error al asignar la variable {variable_name}: {response.status_code}, {response.text}")

    if response.content:
        return response.json()
    else:
        return None

def get_user_id_by_username():
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = f"/API/identity/user?s={username}"
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}'
    }

    response = requests.get(base_url + url, headers=headers)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if isinstance(json_data, list) and len(json_data) > 0:
                return json_data[0]['id']
            else:
                raise ValueError("La respuesta no contiene tareas asociadas al caseId.")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Error al procesar la respuesta JSON: {e}")
    else:
        raise Exception(f"Error al obtener el userId: {response.status_code}, {response.text}")

def assign_user_to_task(task_id, user_id):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = "/API/bpm/userTask/" + str(task_id)
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}',
        'Content-Type': 'application/json'
    }
    payload = {"assigned_id": user_id}

    response = requests.put(base_url + url, headers=headers, json=payload)

    if response.status_code == 200 or response.status_code == 204:
        if response.content:
            return response.json()
        else:
            return None
    else:
        print(f"Error al asignar usuario a la tarea: {response.status_code}, {response.text}")
        raise Exception(f"Error al asignar usuario a la tarea: {response.status_code}, {response.text}")

def complete_task(task_id):
    token = session.get('bonita_token')
    session_id = session.get('session_id')
    url = f"/API/bpm/userTask/{task_id}/execution"
    headers = {
        'X-Bonita-API-Token': token,
        'Cookie': f'JSESSIONID={session_id}; X-Bonita-API-Token={token}'
    }

    response = requests.post(base_url + url, headers=headers)

    if response.status_code == 200 or response.status_code == 204:
        if response.content:
            return response.json()
        else:
            return None
    else:
        print(f"Error al completar la tarea: {response.status_code}, {response.text}")
        raise Exception(f"Error al completar la tarea: {response.status_code}, {response.text}")
