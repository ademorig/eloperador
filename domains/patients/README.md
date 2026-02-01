# Dominio: Pacientes (`patients`)

Este dominio es el sistema de registro de identidad de pacientes (MPI - Master Patient Index) del Operador.

## 📋 Responsabilidades
1. **Gestión de Identidad**: Creación, búsqueda y actualización de datos demográficos.
2. **Clasificación**: Diferenciar entre pacientes internos (DICOM/HIS) y externos (excepcionales).
3. **Auditoría**: Registro de origen de la creación (ej. "telegram", "manual", "api").

## 🛑 Límites
- **NO** gestiona estudios médicos.
- **NO** gestiona informes.
- **NO** tiene lógica de comunicación.

## 🔐 Seguridad
Los datos demográficos son PHI (Protected Health Information). El acceso está restringido a servicios internos validados.
