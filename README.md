# Proyecto El Operador & n8n Workflows

Este repositorio contiene el sistema de orquestación "El Operador" y los flujos de trabajo de n8n para diversas capacidades del workspace.

## Estructura del Proyecto

El proyecto se ha organizado en los siguientes dominios funcionales:

- **`domains/`**: Contiene la lógica específica de cada área.
    - **`email/`**: Scripts de vigilancia y limpieza de correos (Gmail).
    - **`radiology/`**: Flujos de trabajo relacionados con radiología y PACS.
    - **`telegram/`**: Integraciones y bots de Telegram.
    - **`n8n_management/`**: Herramientas para administrar, corregir e inspeccionar flujos de n8n.
- **`operador/`**: El núcleo del sistema "El Operador" (API, Dashboard, Memoria). **Área Crítica y Asegurada.**
- **`infrastructure/`**: Configuración de despliegue, servicios systemd y MCP.
- **`shared/`**: Utilidades compartidas (clientes API, helpers).
- **`legacy/`**: Código antiguo o deprecado.

## Seguridad y Despliegue

### El Operador
El núcleo se encuentra en `operador/`. 
- **Despliegue**: Usar `master_deploy.py` (requiere `.env`).
- **Configuración**: Copiar `operador/.env.example` a `operador/.env` y configurar credenciales.
- **Servicios**: Archivos `.service` endurecidos disponibles en `operador/` (o `infrastructure/`).

### Requisitos
Ver `requirements.txt` en la raíz o en `operador/` para dependencias específicas.

## Gobernanza
- No mover lógica médica de `domains/radiology` sin revisión.
- Toda nueva automatización debe documentarse en este README o en el dominio correspondiente.
