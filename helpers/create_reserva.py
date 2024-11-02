from helpers.bonita import (
    assign_user_to_task,
    assign_variable_by_task_and_case,
    complete_task,
    get_process_id,
    get_task_by_case,
    init_process, 
)
from flask import session

def create_reserva(cantidad, material_id, fecha):
    try:
        # 1. Obtengo el ID del proceso de la orden
        process_id = get_process_id('Reserva')

        # 2. Instancio el proceso
        case_id = init_process(process_id)

        # 3. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        fabricante_username = session.get('user_name')

        # 4. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'material_id', material_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'cantidad', int(cantidad), 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'fecha_prevista', fecha, 'java.lang.String')
        assign_variable_by_task_and_case(case_id, 'case_id', case_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'fabricante_username', fabricante_username, 'java.lang.String')

        # 5. Asigno la actividad al usuario
        assign_user_to_task(task_id)

        # 6. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        print(f"Proceso de reserva creado con éxito, caso: {case_id}")

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")