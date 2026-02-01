# 🛠️ Guía: Cómo Publicar tus Workflows en el Servidor MCP

Si ejecutas `python n8n_manager.py list` y ves el mensaje **"📭 No hay workflows disponibles"**, significa que n8n no está exponiendo tus workflows al protocolo MCP. 

Sigue estos pasos para solucionarlo:

### 1. Tag "mcp" (Vital)
El servidor MCP de n8n suele filtrar los workflows por una etiqueta.
1. En n8n, abre tu workflow (`Radiology_Shift_Organizer_Agent` o `MCP_CheckAndScheduleEvent`).
2. En la barra superior, haz clic en **"Tags"**.
3. Escribe `mcp` y presiona Enter.
4. Guarda el workflow.

### 2. Activar el Workflow
Los triggers de tipo Webhook (usados por MCP) **solo funcionan si el workflow está activo**.
1. Asegúrate de que el interruptor en la esquina superior derecha diga **"Workflow is active"** (en verde 🟢).

### 3. Configurar el Trigger Correctamente
Tu nodo de entrada debe ser un **Webhook** o un **MCP Trigger** (si tienes el nodo instalado).
- **Nombre del nodo**: Debe ser descriptivo (ej: `MCP Trigger`).
- **HTTP Method**: POST.
- **Path**: Debe ser único (ej: `radiology-search`).

### 4. Credenciales de Gmail / Google Calendar
Si el nodo dice "Credential not set":
1. Ve a **Credentials** en n8n.
2. Busca la credencial que creaste.
3. Asegúrate de que el nombre coincida con lo que el nodo espera.
4. **IMPORTANTE**: Abre el nodo de Gmail en el workflow y vuelve a seleccionar la credencial en el menú desplegable, incluso si parece seleccionada. Luego dale a **"Test Step"** para verificar que funciona.

---

## 🧪 Cómo verificar si funcionó
Una vez hecho lo anterior, corre este comando en tu terminal:

```bash
python n8n_manager.py list
```

Si ahora ves una lista con tus workflows, ¡ya puedes pedirle a Antigravity que los use!
