"""
Custom error classes and error handling utilities
"""
from flask import jsonify
from functools import wraps

class HardwareError(Exception):
    """Raised when hardware monitoring fails"""
    pass

class MetricUnavailableError(Exception):
    """Raised when a metric cannot be retrieved"""
    pass

def handle_api_errors(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except MetricUnavailableError as e:
            return jsonify({"error": str(e)}), 503
        except HardwareError as e:
            return jsonify({"error": f"Hardware error: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    return decorated_function

