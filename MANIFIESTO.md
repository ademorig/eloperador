# Manifiesto del Proyecto: El Operador

Este documento define la estructura, gobernanza y dominios funcionales del workspace. Actúa como la fuente de verdad para la organización y seguridad del sistema.

## 1. Identidad y Propósito
"El Operador" es un sistema de automatización y asistencia que integra múltiples capacidades críticas: comunicación, vigilancia, medicina y gestión administrativa.

## 2. Dominios Funcionales

### 📡 Comunicación y Alertas (`domains/communication`)
- **Responsabilidad**: Gestión de interacciones, recepción de comandos y notificaciones vía Telegram. Servidor de Dashboard.
- **Componentes**: `telegram_listener.py`, `telegram_operator.py`, `dashboard_server.py`.
- **Estado**: Activo / Estable.

### 📧 Vigilancia de Correos (`domains/email`)
- **Responsabilidad**: Monitoreo de bandejas de entrada, alertas de urgencia y mantenimiento de limpieza.
- **Componentes**: Scripts de limpieza y vigilancia.
- **Estado**: Activo.

### 📅 Gestión de Calendarios (`domains/scheduling`)
- **Responsabilidad**: Creación, revisión y sincronización de agendas y turnos.
- **Componentes**: Workflows de n8n y herramientas MCP.
- **Estado**: Activo.

### 🏥 Flujos de Radiología (`domains/radiology`)
- **Responsabilidad**: Procesamiento de estudios, descarga y organización de flujos médicos.
- **Estado**: **CRÍTICO / SENSIBLE**.
- **Restricción**: Solo lectura para procesos automáticos no verificados. No mover lógica sin validación médica.

### 📄 Reportes de Pacientes (`domains/patient_reports`)
- **Responsabilidad**: Generación y entrega proactiva de informes a pacientes.
- **Estado**: Estructura lista / En desarrollo.

## 3. Estructura del Sistema (Gobernanza)

### 📂 Núcleo (`core/`)
- `infrastructure/`: Despliegue (`master_deploy.py`), archivos de servicio systemd y configuración MCP.
- `memory/`: Gestión de estado persistente con bloqueo de archivos (`memory_manager.py`).
- `security/`: Validación de secretos (.env) y entorno.

### 📂 Operaciones (`scripts/`)
- `n8n_management/`: Utilidades para mantenimiento y manipulación de workflows n8n.
- `test/`: Pruebas de integración y conectividad.

### 📂 Histórico (`legacy/`)
- Contiene código antiguo o versiones previas que no deben ser borradas por trazabilidad.
- **Regla**: Prohibido el borrado, solo archivado.

## 4. Clasificación de Acceso y Modificación

| Tipo de Archivo | Ubicación | Permiso | Nota |
| :--- | :--- | :--- | :--- |
| **Lógica Médica** | `domains/radiology` | Solo Lectura | Marcado como crítico. |
| **Infraestructura** | `core/infrastructure`| Restringido | Requiere validación DevSecOps. |
| **Utilidades** | `scripts/*` | Modificable | Para mantenimiento diario. |
| **Legacy** | `legacy/*` | Solo Lectura | No borrar. |

## 5. Changelog de Seguridad y Estructura
- **2026-01-31**: Alineación total con el rol de Arquitecto de Sistema.
- **2026-01-31**: Hardening DevSecOps finalizado:
    - Centralización de secretos en `.env` (puertos, hosts, rutas).
    - Refactorización de `master_deploy.py` para despliegue limpio.
    - Sandboxing de servicios systemd (`NoNewPrivileges`, `ProtectSystem=full`, `ProtectHome=true`).
    - Implementación de bloqueo de archivos (Locking) en `memory_manager.py` para evitar corrupción concurrente.
- **2026-01-31**: Reorganización de carpetas:
    - Integración de `infrastructure/mcp` en `core/infrastructure/mcp`.
    - Creación de dominio `domains/patient_reports`.
    - Eliminación de directorios redundantes.

---
*Gobernanza establecida por Antigravity - Arquitecto del Sistema.*
