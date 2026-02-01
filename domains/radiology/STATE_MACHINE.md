# Estados de Flujo de Radiología (Estándar Sirius RIS)

Para asegurar la interoperabilidad y claridad en la gestión de estudios, "El Operador" adopta los siguientes estados de flujo:

| Código | Estado | Descripción |
| :--- | :--- | :--- |
| **P01** | Recepción | El paciente ha llegado y ha sido registrado. |
| **P02** | Entrevista | Se ha completado la anamnesis o entrevista previa. |
| **P03** | Preparación | El paciente está bajo preparación (ayuno, inyección, etc.). |
| **P04** | Adquisición | El estudio se está realizando en la modalidad (CT, MRI, RX). |
| **P05** | Verificación | Control de calidad de las imágenes adquiridas. |
| **P06** | Para informar | El estudio está disponible en el PACS para reporte médico. |
| **P07** | Informe borrador | El radiólogo ha iniciado el dictado pero no lo ha firmado. |
| **P08** | Informe firmado | El reporte ha sido validado por el especialista. |
| **P09** | Terminado (C/I) | Estudio cerrado con informe disponible para entrega. |
| **P10** | Terminado (S/I) | Estudio cerrado sin necesidad de informe. |
| **P11** | Cancelado | El estudio fue anulado. |

> [!NOTE]
> Estos estados deben ser utilizados en los metadatos de los workflows de n8n para permitir filtrado y búsqueda inteligente.
