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

def create_reserva(token, cantidad, materia_id, fecha):
    try:
        # TODO
        return
    except Exception as e:
        raise Exception(f"Error en el proceso de Bonita: {str(e)}")