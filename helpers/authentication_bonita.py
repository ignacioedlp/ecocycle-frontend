from helpers.bonita import (
    authenticate,
    get_role_info,
    get_user_info,
    get_membership_info
)

def authentication_bonita(username, password):
    try:
        authenticate(username, password)
        get_user_info()
        get_membership_info()
        get_role_info()
        
        return True
    except Exception as e:
        raise Exception(f"Error proceso de authenticacion: {str(e)}")