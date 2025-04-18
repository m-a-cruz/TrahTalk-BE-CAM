from flask import Blueprint
from app.controller import insight
from app.management.middleware import handle_errors, protected_route

insight_bp = Blueprint('insight', __name__, url_prefix='/api/insight')

@insight_bp.route('/forcast', methods=['GET'], endpoint='get_forcast_insight')
@handle_errors
def get_forcast_insight(): return insight.fetch_insight()