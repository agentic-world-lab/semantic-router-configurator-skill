# Semantic Router Configurator Skill

## Overview
This skill provides an intelligent configuration generator for the vLLM Semantic Router project. It helps users create proper configuration files for semantic routing based on their specific requirements and use cases.

## Purpose
The Semantic Router Configurator Skill enables agents to:
- Generate valid configuration files for the vLLM Semantic Router
- Configure routing decisions with appropriate plugins
- Set up model endpoints and listeners
- Apply best practices for semantic routing setups

## Features
- **Interactive Configuration Generation**: Generate configuration files based on user requirements
- **Plugin Support**: Configure various plugins (semantic-cache, jailbreak, PII detection, hallucination detection, etc.)
- **Validation**: Validate configuration files against semantic router requirements
- **Templates**: Provide pre-configured templates for common use cases

## Usage

### Docker Container
Run the skill as a Docker container:

```bash
docker build -t semantic-router-configurator .
docker run -p 8080:8080 semantic-router-configurator
```

### API Endpoints

#### Generate Configuration
**POST /generate**

Generate a semantic router configuration based on provided parameters.

Request body:
```json
{
  "endpoints": [
    {
      "name": "default",
      "url": "http://localhost:8000/v1/chat/completions"
    }
  ],
  "plugins": [
    {
      "type": "semantic-cache",
      "enabled": true,
      "similarity_threshold": 0.92
    }
  ],
  "port": 8888
}
```

Response:
```yaml
# Generated semantic router configuration
version: "1.0"
listeners:
  - port: 8888
    endpoints:
      - name: default
        url: http://localhost:8000/v1/chat/completions
decisions:
  - name: default_route
    endpoint: default
    plugins:
      - type: semantic-cache
        configuration:
          enabled: true
          similarity_threshold: 0.92
```

#### Validate Configuration
**POST /validate**

Validate a semantic router configuration file.

Request body:
```json
{
  "config": "version: \"1.0\"\nlisteners:\n  - port: 8888"
}
```

Response:
```json
{
  "valid": true,
  "errors": []
}
```

## Configuration Options

### Supported Plugins
1. **semantic-cache** - Cache similar requests for performance
2. **jailbreak** - Detect and block adversarial prompts
3. **pii** - Detect and enforce PII policies
4. **system_prompt** - Inject custom system prompts
5. **header_mutation** - Add/modify HTTP headers
6. **hallucination** - Detect hallucinations in responses
7. **router_replay** - Record routing decisions for debugging

### Example Configurations

#### Basic Configuration
```yaml
version: "1.0"
listeners:
  - port: 8888
    endpoints:
      - name: default
        url: http://localhost:8000/v1/chat/completions
decisions:
  - name: default_route
    endpoint: default
```

#### Configuration with Caching
```yaml
version: "1.0"
listeners:
  - port: 8888
    endpoints:
      - name: default
        url: http://localhost:8000/v1/chat/completions
decisions:
  - name: cached_route
    endpoint: default
    plugins:
      - type: semantic-cache
        configuration:
          enabled: true
          similarity_threshold: 0.92
          ttl_seconds: 3600
```

#### Configuration with Multiple Plugins
```yaml
version: "1.0"
listeners:
  - port: 8888
    endpoints:
      - name: gpt4
        url: http://localhost:8001/v1/chat/completions
      - name: gpt3
        url: http://localhost:8002/v1/chat/completions
decisions:
  - name: secure_route
    endpoint: gpt4
    plugins:
      - type: jailbreak
        configuration:
          enabled: true
          threshold: 0.8
      - type: pii
        configuration:
          enabled: true
          threshold: 0.7
      - type: semantic-cache
        configuration:
          enabled: true
          similarity_threshold: 0.92
```

## Integration with kagent
This skill is designed to be used by agents through the kagent framework. The skill exposes a RESTful API that agents can call to generate and validate semantic router configurations.

## Requirements
- Python 3.9+
- Docker (for containerized deployment)
- vLLM Semantic Router project (for testing generated configurations)

## Development
See the main repository for development guidelines and contribution instructions.
