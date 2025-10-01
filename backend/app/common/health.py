from flask import Blueprint, jsonify
from datetime import datetime, timezone

__uri__ = 'common'
__blueprint__ = 'common'

common = Blueprint(__uri__, __name__)

@common.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to monitor uptime.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200