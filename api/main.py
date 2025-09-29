"""
API Cloud Function - Main entry point for HTTP requests
"""
import functions_framework
from flask import Request
import json
from shared.database import get_db_connection
from shared.utils import logger


@functions_framework.http
def api_handler(request: Request):
    """HTTP Cloud Function entry point"""
    
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Route based on path
        path = request.path.strip('/')
        method = request.method
        
        logger.info(f"API request: {method} /{path}")
        
        if path.startswith('predictions'):
            return handle_predictions(request, path, method), 200, headers
        elif path.startswith('data'):
            return handle_data(request, path, method), 200, headers
        else:
            return {'error': 'Not found'}, 404, headers
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return {'error': 'Internal server error'}, 500, headers


def handle_predictions(request: Request, path: str, method: str):
    """Handle prediction-related endpoints"""
    if method == 'GET':
        # Get predictions
        return {'predictions': []}
    elif method == 'POST':
        # Create prediction
        data = request.get_json()
        return {'message': 'Prediction created', 'data': data}
    
    return {'error': 'Method not allowed'}, 405


def handle_data(request: Request, path: str, method: str):
    """Handle data-related endpoints"""
    if method == 'GET':
        # Get data
        return {'data': []}
    
    return {'error': 'Method not allowed'}, 405
