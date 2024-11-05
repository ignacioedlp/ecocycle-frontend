from helpers.bonita import (
    assign_user_to_task,
    assign_variable_by_task_and_case,
    complete_task,
    get_process_id,
    get_task_by_case,
    init_process, 
)
from flask import session

def add_recoleccion(material_id, cantidad, deposito_id, punto_de_recoleccion_id):
    try:
        # 2. Obtengo el ID del proceso de la orden
        process_id = get_process_id('Recoleccion')

        # 3. Instancio el proceso
        case_id = init_process(process_id)

        # 4. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        recolector_username = session.get('user_name')

        # 5. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'recolector_username', recolector_username, 'java.lang.String')
        assign_variable_by_task_and_case(case_id, 'material_id', material_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'cantidad', int(cantidad), 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'deposito_id', deposito_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'punto_de_recoleccion_id', punto_de_recoleccion_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'case_id', case_id, 'java.lang.Integer')

        # 6 Asigno la actividad al usuario
        assign_user_to_task(task_id)

        # 7. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        print(f"Proceso de recolección creado con éxito, caso: {case_id}")

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")
