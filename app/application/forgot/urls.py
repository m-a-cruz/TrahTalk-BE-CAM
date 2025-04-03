from flask import Blueprint,jsonify
import application.forgot.forgot as forgot

reset_bp = Blueprint('reset', __name__, url_prefix='/reset')

@reset_bp.route('/forgot', methods=['POST'])
def forgot_password():
    return forgot.forgot_password()

@reset_bp.route('/forgot-reset', methods=['POST'])
def reset_password():
    return forgot.reset_password()