# 🔧 Estilo de Codigo - Frontend

# 💻 Guía de Estilo de Código — ESLint (JavaScript)

**ESLint** es una herramienta (linter) que analiza el código JavaScript para encontrar errores, inconsistencias y violaciones a las reglas de estilo definidas por la comunidad o el equipo de desarrollo.  
Ayuda a mantener un código **limpio, legible y coherente**.

---

## 🧩 1. ¿Qué es ESLint?

- Es una **librería de análisis estático** que revisa tu código sin ejecutarlo.
- Detecta:
  - Errores de sintaxis.
  - Variables no utilizadas.
  - Malas prácticas.
  - Estilos inconsistentes (espacios, comillas, etc.).
- Puede **corregir automáticamente** ciertos errores con:
  ```bash
  npx eslint . --fix
  ```

---

## ⚙️ 2. Instalación y configuración básica

Instalar ESLint como dependencia de desarrollo:
```bash
npm install eslint --save-dev
```

Inicializar la configuración:
```bash
npx eslint --init
```

Esto crea un archivo de configuración (`.eslintrc.json`, `.eslintrc.js`, etc.) donde se definen las reglas.

Ejemplo básico (`.eslintrc.json`):
```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "rules": {
    "semi": ["error", "always"],
    "quotes": ["error", "double"],
    "no-unused-vars": "warn"
  }
}
```


