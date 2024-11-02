from helpers.bonita import (
    authenticate,
    get_role_info,
    get_user_info,
    get_membership_info
)

def authentication(username, password):
    try:
        authenticate(username, password)
        get_user_info()
        get_membership_info()
        get_role_info()
        
        print(f"Proceso de authenticacion completado")

        return True
    except Exception as e:
        raise Exception(f"Error proceso de authenticacion: {str(e)}")