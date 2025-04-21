from flask import Blueprint
from app.controller import camera
from app.management.middleware import handle_errors, protected_route

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')

@camera_bp.route('/upload', methods=['POST'], endpoint='upload_image')
@handle_errors 
def upload_image(): return camera.upload_image()

# @camera_bp.route('/process', methods=['GET'], endpoint='process_latest')
# @handle_errors
# def process_latest(): return camera.process_latest()