"""
Semantic Router Configurator Skill

A Flask-based API service for generating and validating semantic router configurations.
"""

from flask import Flask, request, jsonify, Response
import yaml
import logging
from typing import Dict, List, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Supported plugin types
SUPPORTED_PLUGINS = [
    'semantic-cache',
    'jailbreak',
    'pii',
    'system_prompt',
    'header_mutation',
    'hallucination',
    'router_replay'
]

# Plugin configuration schemas
PLUGIN_SCHEMAS = {
    'semantic-cache': {
        'required': ['enabled'],
        'optional': ['similarity_threshold', 'ttl_seconds']
    },
    'jailbreak': {
        'required': ['enabled'],
        'optional': ['threshold']
    },
    'pii': {
        'required': ['enabled'],
        'optional': ['threshold', 'pii_types_allowed']
    },
    'system_prompt': {
        'required': ['enabled'],
        'optional': ['system_prompt', 'mode']
    },
    'header_mutation': {
        'required': [],
        'optional': ['add', 'update', 'delete']
    },
    'hallucination': {
        'required': ['enabled'],
        'optional': ['use_nli', 'hallucination_action']
    },
    'router_replay': {
        'required': ['enabled'],
        'optional': ['max_records', 'capture_request_body', 'capture_response_body', 'max_body_bytes']
    }
}

# Configuration templates
CONFIGURATION_TEMPLATES = {
    'basic': {
        'name': 'Basic Configuration',
        'description': 'Simple single-endpoint configuration',
        'config': {
            'version': '1.0',
            'port': 8888,
            'endpoints': [
                {
                    'name': 'default',
                    'url': 'http://localhost:8000/v1/chat/completions'
                }
            ]
        }
    },
    'cached': {
        'name': 'Cached Configuration',
        'description': 'Configuration with semantic caching enabled',
        'config': {
            'version': '1.0',
            'port': 8888,
            'endpoints': [
                {
                    'name': 'default',
                    'url': 'http://localhost:8000/v1/chat/completions'
                }
            ],
            'plugins': [
                {
                    'type': 'semantic-cache',
                    'configuration': {
                        'enabled': True,
                        'similarity_threshold': 0.92,
                        'ttl_seconds': 3600
                    }
                }
            ]
        }
    },
    'secure': {
        'name': 'Secure Configuration',
        'description': 'Configuration with security plugins enabled',
        'config': {
            'version': '1.0',
            'port': 8888,
            'endpoints': [
                {
                    'name': 'default',
                    'url': 'http://localhost:8000/v1/chat/completions'
                }
            ],
            'plugins': [
                {
                    'type': 'jailbreak',
                    'configuration': {
                        'enabled': True,
                        'threshold': 0.8
                    }
                },
                {
                    'type': 'pii',
                    'configuration': {
                        'enabled': True,
                        'threshold': 0.7
                    }
                }
            ]
        }
    },
    'multi-model': {
        'name': 'Multi-Model Configuration',
        'description': 'Configuration with multiple model endpoints',
        'config': {
            'version': '1.0',
            'port': 8888,
            'endpoints': [
                {
                    'name': 'gpt4',
                    'url': 'http://localhost:8001/v1/chat/completions'
                },
                {
                    'name': 'gpt3',
                    'url': 'http://localhost:8002/v1/chat/completions'
                }
            ],
            'plugins': [
                {
                    'type': 'semantic-cache',
                    'configuration': {
                        'enabled': True,
                        'similarity_threshold': 0.92
                    }
                }
            ]
        }
    }
}


def validate_plugin(plugin: Dict[str, Any]) -> List[str]:
    """Validate a single plugin configuration."""
    errors = []
    
    if 'type' not in plugin:
        errors.append("Plugin missing 'type' field")
        return errors
    
    plugin_type = plugin['type']
    if plugin_type not in SUPPORTED_PLUGINS:
        errors.append(f"Unsupported plugin type: {plugin_type}")
        return errors
    
    if 'configuration' not in plugin:
        errors.append(f"Plugin '{plugin_type}' missing 'configuration' field")
        return errors
    
    config = plugin['configuration']
    schema = PLUGIN_SCHEMAS.get(plugin_type, {})
    
    # Check required fields
    for field in schema.get('required', []):
        if field not in config:
            errors.append(f"Plugin '{plugin_type}' missing required field: {field}")
    
    # Validate field types and values
    if 'enabled' in config and not isinstance(config['enabled'], bool):
        errors.append(f"Plugin '{plugin_type}': 'enabled' must be a boolean")
    
    if 'threshold' in config or 'similarity_threshold' in config:
        threshold = config.get('threshold') or config.get('similarity_threshold')
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            errors.append(f"Plugin '{plugin_type}': threshold must be between 0.0 and 1.0")
    
    if 'ttl_seconds' in config:
        if not isinstance(config['ttl_seconds'], int) or config['ttl_seconds'] < 0:
            errors.append(f"Plugin '{plugin_type}': ttl_seconds must be a non-negative integer")
    
    if 'max_records' in config:
        if not isinstance(config['max_records'], int) or config['max_records'] <= 0:
            errors.append(f"Plugin '{plugin_type}': max_records must be a positive integer")
    
    if 'mode' in config and config['mode'] not in ['replace', 'insert']:
        errors.append(f"Plugin '{plugin_type}': mode must be 'replace' or 'insert'")
    
    return errors


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a semantic router configuration."""
    errors = []
    
    # Check version
    if 'version' not in config:
        errors.append("Configuration missing 'version' field")
    
    # Check listeners
    if 'listeners' not in config:
        errors.append("Configuration missing 'listeners' field")
    else:
        for i, listener in enumerate(config['listeners']):
            if 'port' not in listener:
                errors.append(f"Listener {i} missing 'port' field")
            elif not isinstance(listener['port'], int) or listener['port'] <= 0:
                errors.append(f"Listener {i}: port must be a positive integer")
            
            if 'endpoints' in listener:
                for j, endpoint in enumerate(listener['endpoints']):
                    if 'name' not in endpoint:
                        errors.append(f"Listener {i}, endpoint {j} missing 'name' field")
                    if 'url' not in endpoint:
                        errors.append(f"Listener {i}, endpoint {j} missing 'url' field")
    
    # Check decisions
    if 'decisions' in config:
        for i, decision in enumerate(config['decisions']):
            if 'name' not in decision:
                errors.append(f"Decision {i} missing 'name' field")
            if 'endpoint' not in decision:
                errors.append(f"Decision {i} missing 'endpoint' field")
            
            # Validate plugins
            if 'plugins' in decision:
                for plugin in decision['plugins']:
                    plugin_errors = validate_plugin(plugin)
                    errors.extend([f"Decision {i}: {e}" for e in plugin_errors])
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def generate_config(params: Dict[str, Any]) -> str:
    """Generate a semantic router configuration from parameters."""
    config = {
        'version': params.get('version', '1.0')
    }
    
    # Add listeners
    listeners = []
    port = params.get('port', 8888)
    endpoints = params.get('endpoints', [])
    
    if not endpoints:
        endpoints = [{
            'name': 'default',
            'url': 'http://localhost:8000/v1/chat/completions'
        }]
    
    listener = {
        'port': port,
        'endpoints': endpoints
    }
    listeners.append(listener)
    config['listeners'] = listeners
    
    # Add decisions
    decisions = []
    plugins = params.get('plugins', [])
    
    # Create a decision for each endpoint
    for endpoint in endpoints:
        decision = {
            'name': f"{endpoint['name']}_route",
            'endpoint': endpoint['name']
        }
        
        if plugins:
            decision['plugins'] = plugins
        
        decisions.append(decision)
    
    config['decisions'] = decisions
    
    return yaml.dump(config, default_flow_style=False, sort_keys=False)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/generate', methods=['POST'])
def generate():
    """Generate a semantic router configuration."""
    try:
        params = request.get_json()
        if not params:
            return jsonify({'error': 'Request body is required'}), 400
        
        config_yaml = generate_config(params)
        
        # Parse the generated YAML to validate it
        config_dict = yaml.safe_load(config_yaml)
        validation_result = validate_config(config_dict)
        
        if not validation_result['valid']:
            return jsonify({
                'error': 'Generated configuration is invalid',
                'validation_errors': validation_result['errors']
            }), 400
        
        return Response(config_yaml, mimetype='text/yaml'), 200
    
    except Exception as e:
        logger.error(f"Error generating configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/validate', methods=['POST'])
def validate():
    """Validate a semantic router configuration."""
    try:
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify({'error': 'Request must include "config" field'}), 400
        
        config_str = data['config']
        
        # Parse YAML
        try:
            config_dict = yaml.safe_load(config_str)
        except yaml.YAMLError as e:
            return jsonify({
                'valid': False,
                'errors': [f'Invalid YAML: {str(e)}']
            }), 200
        
        # Validate configuration
        result = validate_config(config_dict)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/templates', methods=['GET'])
def templates():
    """Get available configuration templates."""
    return jsonify(CONFIGURATION_TEMPLATES), 200


@app.route('/templates/<template_name>', methods=['GET'])
def get_template(template_name: str):
    """Get a specific configuration template."""
    try:
        if template_name not in CONFIGURATION_TEMPLATES:
            return jsonify({'error': f'Template "{template_name}" not found'}), 404
        
        template = CONFIGURATION_TEMPLATES[template_name]
        config_yaml = generate_config(template['config'])
        
        return Response(config_yaml, mimetype='text/yaml'), 200
    
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
