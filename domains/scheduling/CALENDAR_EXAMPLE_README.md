# 📅 Ejemplo: Agendamiento de Calendario vía MCP

Este ejemplo muestra cómo crear un workflow en n8n que puede ser llamado desde un agente MCP (como Antigravity) para agendar eventos en Google Calendar.

## 📋 Estructura del Workflow

El workflow `MCP_CheckAndScheduleEvent` realiza los siguientes pasos:

1. **Trigger**: Recibe la solicitud del agente MCP.
2. **Parse**: Extrae los datos del evento (`nombre`, `fecha`, `usuario`).
3. **Verificar**: Busca conflictos en Google Calendar.
4. **Decidir**: Si no hay conflictos, procede a crear el evento.
5. **Responder**: Devuelve un resumen estructurado al agente.

## 🚀 Instrucciones de Uso

1. **Importar el Workflow**:
   - Abre n8n.
   - Crea un nuevo workflow.
   - Importa el archivo `mcp_calendar_workflow.json` (puedes arrastrarlo o pegarlo).

2. **Configurar Credenciales**:
   - Asegúrate de tener configuradas tus credenciales de **Google Calendar** en n8n.
   - En el nodo "Google Calendar", selecciona tus credenciales.

3. **Publicar vía MCP**:
   - Si usas el sistema de servidor MCP de n8n, asegúrate de activar el trigger correspondiente o añadir el workflow a la lista de herramientas permitidas.

4. **Probar con el Cliente**:
   - Puedes usar el comando:
     ```bash
     python n8n_manager.py run MCP_CheckAndScheduleEvent '{"mensaje_texto": "Reunión de marketing mañana 10am", "usuario": "tu-email@example.com", "calendario_id": "primary"}'
     ```

## 📄 JSON de Entrada Esperado

```json
{
  "mensaje_texto": "Texto natural de la solicitud",
  "usuario": "email@usuario.com",
  "calendario_id": "primary"
}
```

## 📤 JSON de Salida

```json
{
  "status": "success",
  "evento_id": "ID_DEL_EVENTO",
  "mensaje_resumen": "Evento agendado exitosamente..."
}
```
