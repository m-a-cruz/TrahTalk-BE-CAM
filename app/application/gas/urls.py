from flask import Blueprint
import application.gas.gasRecord as gasRecord
import application.gas.notification as notification
from flask_jwt_extended import jwt_required

gas_bp = Blueprint('gas', __name__, url_prefix='/gas')

@gas_bp.route('/data', methods=['POST'], endpoint='create_gas_records')
def create_gas_records():
    return gasRecord.record_gas_level()

@gas_bp.route('/notification', methods=['POST'], endpoint='create_notification')
def create_notification():
    return notification.record_notif_data()

@gas_bp.route('/charts', methods=['GET'], endpoint='get_gas_chart')
@jwt_required
def get_gas_chart():
    return gasRecord.fetch_gas_chart()

@gas_bp.route('/notifications', methods=['GET'], endpoint='get_notifications')
@jwt_required
def get_notifications():
    return notification.fetch_notif()
