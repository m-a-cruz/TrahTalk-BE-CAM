from flask import Blueprint
from app.management.middleware import handle_errors
import app.model.predict as predict

predict_bp = Blueprint('predict', __name__, url_prefix='/api/predict')

@predict_bp.route('/predict', methods=['GET'])
@handle_errors
def predict_gas_level(): return predict.predict_gas_level()