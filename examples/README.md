# 📚 Ejemplos de Uso

Esta carpeta contiene ejemplos prácticos para aprender a usar el proyecto n8n + MCP.

## 🎯 Ejemplos Disponibles

### 1. `basic_connection.py` - Conexión Básica
**Nivel:** Principiante  
**Qué hace:** Establece una conexión simple con el servidor MCP y lista las herramientas disponibles.

**Ejecutar:**
```bash
python examples/basic_connection.py
```

**Aprenderás:**
- Cómo conectarte al servidor MCP
- Cómo listar herramientas disponibles
- Estructura básica de un cliente MCP

---

### 2. `list_workflows.py` - Listar Workflows
**Nivel:** Principiante  
**Qué hace:** Muestra todos los workflows disponibles en tu instancia de n8n.

**Ejecutar:**
```bash
python examples/list_workflows.py
```

**Aprenderás:**
- Cómo usar la herramienta `search_workflows`
- Cómo parsear respuestas JSON del servidor
- Cómo filtrar workflows por nombre

**Personalizar:**
- Descomenta el "Ejemplo 2" al final del archivo
- Cambia `"test"` por el nombre que quieras buscar

---

### 3. `execute_workflow.py` - Ejecutar Workflows
**Nivel:** Intermedio  
**Qué hace:** Ejecuta un workflow específico, con o sin parámetros.

**Ejecutar:**
```bash
python examples/execute_workflow.py
```

**⚠️ IMPORTANTE:** Antes de ejecutar, edita el archivo y reemplaza:
```python
WORKFLOW_ID = "YOUR_WORKFLOW_ID"
```

Por el ID real de uno de tus workflows (lo puedes obtener con `list_workflows.py`).

**Aprenderás:**
- Cómo obtener detalles de un workflow antes de ejecutarlo
- Cómo ejecutar workflows sin parámetros
- Cómo pasar datos de entrada a un workflow

**Personalizar:**
- Descomenta el "Ejemplo 3" para ejecutar con parámetros
- Ajusta el diccionario `input_data` según lo que espere tu workflow

---

## 🚀 Orden Recomendado de Aprendizaje

Si eres nuevo, sigue este orden:

1. **`basic_connection.py`** → Verifica que todo funciona
2. **`list_workflows.py`** → Explora tus workflows disponibles
3. **`execute_workflow.py`** → Ejecuta tu primer workflow

## 💡 Tips

### Cómo obtener el ID de un workflow

Ejecuta:
```bash
python examples/list_workflows.py
```

Verás algo como:
```
1. Mi Workflow de Prueba
   ID: abc123-def456-ghi789
   Estado: 🟢 Activo
```

Copia el ID y úsalo en `execute_workflow.py`.

### Cómo saber qué parámetros espera un workflow

Antes de ejecutar un workflow con parámetros, usa `get_workflow_details`:

```bash
python n8n_manager.py info <workflow-id>
```

Esto te mostrará información sobre el trigger y los nodos del workflow.

### Debugging

Si algo no funciona:

1. Verifica que `.env` está configurado correctamente
2. Asegúrate de que n8n está ejecutándose
3. Revisa que el workflow existe y está activo
4. Mira los logs de n8n para más detalles

## 🎓 Próximos Pasos

Una vez que domines estos ejemplos:

1. **Modifica los scripts** para adaptarlos a tus necesidades
2. **Crea tus propios workflows** en n8n
3. **Integra con otras herramientas** (bases de datos, APIs, etc.)
4. **Automatiza tareas repetitivas** desde Python

## 📖 Recursos Adicionales

- [Documentación principal](../README.md)
- [n8n Workflow Examples](https://n8n.io/workflows)
- [MCP Documentation](https://modelcontextprotocol.io/)

---

**¿Tienes dudas?** Revisa el [README principal](../README.md) o la sección de Troubleshooting.
