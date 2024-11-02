from helpers.bonita import (
    assign_user_to_task,
    complete_task,
    get_task_by_case, 
)
from flask import session

def completar_reserva_bonita(case_id):
    try:
        # 1. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        # 4. Asigno la actividad al usuario
        assign_user_to_task(task_id)

        # 5. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        print(f"Proceso de recolección creado con éxito, caso: {case_id}")

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")