# Dominio: Reportes de Pacientes (`patient_reports`)

Este dominio es responsable de la orquestación, generación y entrega proactiva de informes médicos a los pacientes. Actúa como el puente final entre los resultados procesados y el usuario final.

## 📋 Responsabilidades

1.  **Orquestación de Datos**: Recopilar la información necesaria desde otros dominios (ej. `radiology`).
2.  **Generación de Formatos**: Transformar datos crudos en formatos legibles para el paciente (PDF, HTML o mensajes estructurados).
3.  **Gestión de Entrega**: Coordinar con los dominios de `communication` (Telegram) y `email` para el envío efectivo.
4.  **Trazabilidad**: Mantener un registro de qué informes han sido entregados y cuáles están pendientes.

## 🏗️ Estructura del Dominio

-   `controllers/`: Lógica de orquestación y flujo de trabajo.
-   `services/`: Lógica de negocio específica (ej. `report_generator`, `delivery_service`).
-   `models/`: Definición de esquemas de datos para los reportes.
-   `templates/`: Plantillas para la generación de informes.

## 🛑 Límites y Restricciones

-   **NO** procesa lógica médica crítica: Solo consume lo que el dominio `radiology` ya ha validado.
-   **NO** gestiona el transporte directo: Utiliza los servicios de `communication` y `email`.
-   **Sensibilidad**: Maneja Datos de Salud (PHI). Toda persistencia o log dentro de este dominio debe estar anonimizado o cifrado según las políticas del sistema.

## 🚀 Estado: En Desarrollo
Actualmente implementando mocks para pruebas de integración de flujo.
