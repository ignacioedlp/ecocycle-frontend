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

def finish_recoleccion(token, case_id, cantidad):
    try:
        # 1. Me autentico en Bonita
        token_bonita, session_id = authenticate()

        # 2. Busco la actividad por caso
        task_id = get_task_by_case(case_id)

        # 3. Asigno las variables de la actividad
        assign_variable_by_task_and_case(case_id, 'cantidad_final', int(cantidad), 'java.lang.Integer')
        assign_variable_by_task_and_case(case_id, 'token', token, 'java.lang.String')

        # 4. Obtengo el userId del usuario por username
        user_id = get_user_id_by_username()

        # 5. Asigno la actividad al usuario
        assign_user_to_task(task_id, user_id)

        # 6. Completo la actividad asi avanza el proceso
        complete_task(task_id)

        print(f"Proceso de recolección creado con éxito, caso: {case_id}")

        return case_id
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")