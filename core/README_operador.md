# El Operador

> Un agente persistente que cuida, optimiza y prepara el terreno.
> No toma el control, no interrumpe. Observa, sugiere y actúa cuando se le permite.

## Estructura

```
operador/
├── system_prompt.md      # Prompt base v0.3 (3 capas)
├── personality.md        # Definición visual de personalidad
├── decision_log.json     # Sistema de memoria persistente
└── silent_observer_wf.json # Workflow n8n de observación
```

## Uso Rápido

### 1. En Antigravity IDE

Copia el contenido de `system_prompt.md` → Agent Manager → Nueva tarea → Pega como instrucción base.

### 2. En n8n

Importa `silent_observer_wf.json` y configura:
- Credenciales de Gmail
- Credenciales de Google Calendar
- Ajusta el intervalo según prefieras (default: cada 6 horas)

## Flujos Disponibles

| Flujo             | Estado | Descripción                               |
| ----------------- | ------ | ----------------------------------------- |
| Silent Observer   | ✅      | Observa Gmail/Calendar y detecta patrones |
| Pattern Automator | 🔜      | Propone y ejecuta automatizaciones        |
| Decision Learner  | 🔜      | Aprende de tus decisiones                 |

## Filosofía

```
"Si esto se repite, sistematízalo.
 Si es sensible, consúltalo.
 Si es ruido, ignóralo."
```

---

**Versión**: v0.3  
**Entorno**: Google Antigravity IDE + n8n  
**Modelo**: Gemini 3 Pro
