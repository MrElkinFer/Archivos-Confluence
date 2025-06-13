## Trayendo y Actualizando archivos desde confluence

#Introducción
Se desdea bajar archivos en formato **markdown** desde confluence.

1. **Creacion del proyecto**: usando el gestor de paquetes para python **uv**

```Command Prompt
uv init archivos
cd archivos
```

2. **Entorno de trabajo**: mediante **uv** creamos el entorno de trabajo con:

```Command Prompt
uv venv venv
```

---

# Requerimientos:

1. atlassian-python-api
2. markdownify
3. dotenv
