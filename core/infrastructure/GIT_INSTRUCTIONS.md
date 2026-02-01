# Gestión de Versiones y Despliegue - El Operador

Este documento define la estrategia para mantener el código organizado entre tu laptop de desarrollo y el VPS de producción.

## 1. Estrategia de Ramas (Branching)

Para evitar subir código "a medio cocinar" al servidor, usaremos dos ramas principales:

*   **`main`**: Rama estable y de producción. Es la que el VPS siempre debe tener.
*   **`dev`**: Rama de desarrollo. Aquí es donde haces cambios grandes, pruebas y experimentos.

### Flujo de Trabajo en Laptop:
```powershell
# 1. Crear o cambiar a la rama dev
git checkout -b dev

# 2. Realizar cambios y commit
git add .
git commit -m "Mejora: Descripción clara del cambio"

# 3. Subir a GitHub para respaldo
git push origin dev

# 4. Cuando el cambio esté sólido, fusionar a main
git checkout main
git merge dev
git push origin main
```

## 2. Versiones con Tags (Snapshot de Seguridad)

Usa etiquetas (tags) para marcar puntos en el tiempo donde el proyecto funciona perfectamente. Esto permite hacer "rollbacks" (volver atrás) sin drama si algo falla en el VPS.

```powershell
# Crear una versión importante
git tag v1.0-radiologia
git push origin v1.0-radiologia

# Si algo sale mal en el VPS y quieres volver a esa versión:
git checkout v1.0-radiologia
```

## 3. Despliegue en el VPS

En el VPS, el flujo es de **solo lectura** desde el repositorio oficial:

```bash
# Actualizar el código
git checkout main
git pull origin main

# Reiniciar servicios para aplicar cambios
sudo systemctl restart operador-listener
sudo systemctl restart operador-dashboard
```

---

## 4. Configuración Inicial (Recordatorio)

### Inicializar Git local
```powershell
git init
git add .
git commit -m "Initial commit: El Operador v0.3"
git branch -M main
```

### Configurar Remote (GitHub/VPS)
```powershell
git remote add origin https://github.com/TU_USUARIO/operador.git
```

### Gestión de Secretos (.env)
**IMPORTANTE**: El archivo `.env` nunca se sube. Asegúrate de que esté en el `.gitignore`.
*   **Laptop**: Configuración de desarrollo.
*   **VPS**: Configuración de producción.

---
*Instrucciones afinadas para un flujo de trabajo profesional y seguro.*
