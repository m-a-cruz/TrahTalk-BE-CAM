from flask import Blueprint
import app.controller.auth as auth
import app.controller.forgot as forgot
from app.management.middleware import handle_errors

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'], endpoint='auth_register')
@handle_errors
def register_user(): return auth.register()

@auth_bp.route('/login', methods=['POST'], endpoint='auth_login')
@handle_errors
def login_user(): return auth.login()

@auth_bp.route('/logout', methods=['POST'], endpoint='auth_logout')
@handle_errors
def logout(): return auth.logout()

@auth_bp.route('/forgot', methods=['POST'], endpoint='forgot_password_endpoint')
@handle_errors
def forgot_password(): return forgot.forgot_password()

@auth_bp.route('/forgot-reset', methods=['POST'], endpoint='reset_user_password_endpoint')
@handle_errors
def reset_user_password(): return forgot.reset_password()