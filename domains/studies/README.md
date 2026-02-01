# Dominio: Estudios (`studies`)

Este dominio gestiona el ciclo de vida de los estudios de imagenología (órdenes médicas).

## 📋 Responsabilidades
1. **Registro de Órdenes**: Creación de estudios vinculados a un `patient_id`.
2. **Estado del Flujo**: Controlar estados como `pending_report`, `reporting`, `completed`.
3. **Metadatos Técnicos**: Región anatómica, tipo de estudio (TAC, RX, RM), médico solicitante.

## 🛑 Límites
- **NO** almacena datos demográficos del paciente (solo el ID).
- **NO** genera el contenido del informe (esto lo hace `patient_reports`).

## 🚀 Atributo Especial: `exceptional_admission`
Los estudios creados vía flujo de emergencia deben marcarse con `exceptional_admission: true` para su posterior auditoría y validación administrativa.
