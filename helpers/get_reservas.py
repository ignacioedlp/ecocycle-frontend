from helpers.bonita import (
    assign_user_to_task,
    assign_variable_by_task_and_case,
    complete_task,
    get_task_by_case,
    get_variable,
    get_process_id,
    init_process,

)
from flask import session
import time
import json

def get_reservas(fecha_inicio, fecha_fin, material_id):
    try:
        process_id = get_process_id('ConsultarReservas')

        # 3. Instancio el proceso
        case_id = init_process(process_id)

        if not case_id:
            raise Exception("Error al instanciar el proceso")

        # 5. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        # 2. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'fecha_inicio', fecha_inicio, 'java.lang.String')
        assign_variable_by_task_and_case(case_id, 'fecha_fin', fecha_fin, 'java.lang.String')
        assign_variable_by_task_and_case(case_id, 'material_id', str(material_id), 'java.lang.String')

        # 4. Asigno la actividad al usuario
        assign_user_to_task(task_id)

        # 5. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        # 6. Espero 5 segundos
        time.sleep(5)

        # 7. Consulto por una variable del mismo caso
        reservas_string = get_variable(case_id, 'reservas_json')

        reservas_json = json.loads(reservas_string)

        task_id = get_task_by_case(case_id)
        assign_user_to_task(task_id)
        complete_task(task_id)

        return reservas_json

    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")