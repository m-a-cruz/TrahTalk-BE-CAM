from flask import Blueprint
from app.controller import camera
from flask_jwt_extended import jwt_required
from app.management.middleware import handle_errors

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')

@camera_bp.route('/upload', methods=['POST'], endpoint='upload_image')
@handle_errors 
def upload_image(): return camera.upload_image()

@camera_bp.route('/latest', methods=['GET'], endpoint='view_latest_image')
@jwt_required
@handle_errors
def view_latest_image(): return camera.view_latest_image()