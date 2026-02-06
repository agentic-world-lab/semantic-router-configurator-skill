# Semantic Router Configurator Skill

Agentic Skill to generate proper configuration for the [vLLM Semantic Router](https://github.com/agentic-world-lab/semantic-router) project.

## Overview

This skill provides an intelligent configuration generator for the vLLM Semantic Router project. It helps users create proper configuration files for semantic routing based on their specific requirements and use cases. The skill exposes a RESTful API that can be used by agents (via kagent) to generate, validate, and manage semantic router configurations.

## Features

- 🚀 **Configuration Generation**: Automatically generate valid semantic router configurations
- ✅ **Validation**: Validate existing configurations against semantic router requirements
- 📋 **Templates**: Pre-configured templates for common use cases
- 🔌 **Plugin Support**: Full support for all semantic router plugins
- 🐳 **Dockerized**: Ready-to-deploy containerized application
- 🔗 **API-First**: RESTful API for easy integration with agents

## Quick Start

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t semantic-router-configurator .
```

2. Run the container:
```bash
docker run -p 8080:8080 semantic-router-configurator
```

3. The API will be available at `http://localhost:8080`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## API Documentation

### Health Check
```bash
GET /health
```

Returns the health status of the service.

### Generate Configuration
```bash
POST /generate
Content-Type: application/json

{
  "version": "1.0",
  "port": 8888,
  "endpoints": [
    {
      "name": "default",
      "url": "http://localhost:8000/v1/chat/completions"
    }
  ],
  "plugins": [
    {
      "type": "semantic-cache",
      "configuration": {
        "enabled": true,
        "similarity_threshold": 0.92,
        "ttl_seconds": 3600
      }
    }
  ]
}
```

Returns a YAML configuration file.

### Validate Configuration
```bash
POST /validate
Content-Type: application/json

{
  "config": "version: \"1.0\"\nlisteners:\n  - port: 8888\n    endpoints:\n      - name: default\n        url: http://localhost:8000/v1/chat/completions"
}
```

Returns validation results with any errors found.

### List Templates
```bash
GET /templates
```

Returns all available configuration templates.

### Get Specific Template
```bash
GET /templates/{template_name}
```

Returns the configuration for a specific template (e.g., `basic`, `cached`, `secure`, `multi-model`).

## Supported Plugins

The configurator supports all vLLM Semantic Router plugins:

1. **semantic-cache** - Cache similar requests for performance
2. **jailbreak** - Detect and block adversarial prompts
3. **pii** - Detect and enforce PII policies
4. **system_prompt** - Inject custom system prompts
5. **header_mutation** - Add/modify HTTP headers
6. **hallucination** - Detect hallucinations in responses
7. **router_replay** - Record routing decisions for debugging

## Example Usage

### Generate a Basic Configuration
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "port": 8888,
    "endpoints": [
      {
        "name": "default",
        "url": "http://localhost:8000/v1/chat/completions"
      }
    ]
  }'
```

### Get a Template
```bash
curl http://localhost:8080/templates/cached
```

### Validate a Configuration
```bash
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{
    "config": "version: \"1.0\"\nlisteners:\n  - port: 8888"
  }'
```

## Integration with kagent

This skill is designed to be used by agents through the kagent framework. Agents can call the API endpoints to:

1. Generate configurations based on user requirements
2. Validate configurations before deployment
3. Retrieve pre-configured templates for common scenarios
4. Customize configurations with specific plugins

## Development

### Running Tests
```bash
# TODO: Add tests
pytest
```

### Code Structure
- `app.py` - Main Flask application with all API endpoints
- `skill.md` - Skill documentation and specification
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See the main repository for license information.

## Related Projects

- [vLLM Semantic Router](https://github.com/agentic-world-lab/semantic-router) - The main semantic router project
- [vLLM Documentation](https://vllm-semantic-router.com/) - Complete documentation for semantic routing
