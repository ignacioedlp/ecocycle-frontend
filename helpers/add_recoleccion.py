from helpers.bonita import (
    assign_user_to_task,
    assign_variable_by_task_and_case,
    authenticate,
    complete_task,
    get_process_id,
    get_task_by_case,
    get_user_id_by_username, 
    init_process, 
)

def add_recoleccion(token, recolector_id, material_id, cantidad, deposito_id):
    try:
        # 1. Me autentico en Bonita
        token_bonita, session_id = authenticate()

        # 2. Obtengo el ID del proceso de la orden
        process_id = get_process_id('Recoleccion')

        # 3. Instancio el proceso
        case_id = init_process(process_id)

        # 5. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        # 6. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'recolector_id', recolector_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'material_id', material_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'cantidad', int(cantidad), 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'deposito_id', deposito_id, 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'token', token, 'java.lang.String')
        assign_variable_by_task_and_case(case_id, 'case_id', case_id, 'java.lang.Integer')

        # 7. Obtengo el userId del usuario por username
        user_id = get_user_id_by_username()

        # 8. Asigno la actividad al usuario
        assign_user_to_task(task_id, user_id)

        # 9. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        print(f"Proceso de recolección creado con éxito, caso: {case_id}")

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")
