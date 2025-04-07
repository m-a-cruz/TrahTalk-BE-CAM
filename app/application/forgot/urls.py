from flask import Blueprint
import application.forgot.forgot as forgot

reset_bp = Blueprint('reset', __name__, url_prefix='/reset')

# @reset_bp.route('/forgot', methods=['POST'])
# def forgot_password():
#     return forgot.forgot_password()

# @reset_bp.route('/forgot-verify', methods=['POST'])
# def reset_password():
#     return forgot.security_code_verification()

# @reset_bp.route('/forgot-reset', methods=['POST'])
# def reset_password():
#     return forgot.reset_password()


@reset_bp.route('/forgot', methods=['POST'], endpoint='forgot_password_endpoint')
def forgot_password():
    return forgot.forgot_password()

@reset_bp.route('/forgot-verify', methods=['POST'], endpoint='verify_reset_token_endpoint')
def verify_reset_token():
    return forgot.security_code_verification()

@reset_bp.route('/forgot-reset', methods=['POST'], endpoint='reset_user_password_endpoint')
def reset_user_password():
    return forgot.reset_password()