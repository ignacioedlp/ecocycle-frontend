from helpers.bonita import (
    assign_user_to_task,
    assign_variable_by_task_and_case,
    complete_task,
    get_task_by_case, 
)
from flask import session

def finish_recoleccion(case_id, cantidad):
    try:
        # 1. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        empleado_username = session.get('user_name')

        # 2. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'cantidad_final', int(cantidad), 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'empleado_username', empleado_username, 'java.lang.String')

        # 4. Asigno la actividad al usuario
        assign_user_to_task(task_id)

        # 5. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")