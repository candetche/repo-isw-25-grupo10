# 🐍 Guía de Estilo de Código — PEP 8 - BACKEND

La **PEP 8** (Python Enhancement Proposal 8) define las **buenas prácticas de estilo** para escribir código Python legible, coherente y mantenible.  
A continuación se presenta un resumen de las reglas más importantes.

---

## 🧩 1. Nombres y Convenciones

### Variables y funciones
- Usar **snake_case** → `nombre_variable`, `calcular_promedio()`
- Evitar abreviaturas innecesarias.
- Las variables privadas comienzan con `_` → `_contador`

### Clases
- Usar **CamelCase** → `class MiClaseEjemplo:`

### Constantes
- Usar **MAYÚSCULAS_CON_GUIONES_BAJOS** → `PI = 3.14159`

---

## 📏 2. Longitud de línea
- Máximo **79 caracteres por línea** (o 72 en comentarios/docstrings).
- Si una línea es muy larga, usar **paréntesis** para dividirla, no `\`.

```python
resultado = funcion_larga(
    argumento_1, argumento_2, argumento_3
)
```

---

## 🧠 3. Indentación
- Usar **4 espacios por nivel de indentación**.
- **No usar tabulaciones** (`\t`).

```python
def ejemplo():
    if True:
        print("Correcto")
```

---

## ✍️ 4. Espacios en blanco

### Dentro de expresiones  
❌ `x=1+2`  
✅ `x = 1 + 2`

### En listas y diccionarios  
❌ `[1,2,3]`  
✅ `[1, 2, 3]`

### Alrededor de paréntesis o índices  
❌ `funcion( 1, 2 )`  
✅ `funcion(1, 2)`

---

## 💬 5. Comentarios

- Deben ser **claros y útiles**.  
- Usar español o inglés, pero **mantener consistencia**.  
- Evitar obviedades.

```python
# Calcula el promedio de una lista
def promedio(lista):
    return sum(lista) / len(lista)
```

### Docstrings
Usar triple comillas (`"""`) para documentar módulos, clases y funciones.

```python
def sumar(a, b):
    """Devuelve la suma de a y b."""
    return a + b
```

---

## 🧱 6. Importaciones

- Cada importación en una línea:

```python
import os
import sys
```

- Orden sugerido:
  1. Librerías estándar  
  2. Librerías de terceros  
  3. Módulos locales  

Con una línea en blanco entre grupos:

```python
import os
import sys

import numpy as np

from mi_paquete import modulo
```

---

## ⚙️ 7. Estructura general

- Definir **funciones y clases** al inicio del archivo.  
- Usar **2 líneas en blanco** entre definiciones de funciones y clases.  
- Bloques internos separados por **una línea en blanco**.

---

## ✅ 8. Comparaciones y booleanos

- Comparar con `None` usando `is` o `is not`.

```python
if variable is None:
    ...
```

- Evitar comparaciones redundantes:

```python
if variable:  # en lugar de if variable == True
```

---

## 🧩 9. Manejo de excepciones

- Específicas y claras:

```python
try:
    resultado = 10 / x
except ZeroDivisionError:
    print("No se puede dividir por cero.")
```

---
# 💻 Guía de Estilo de Código — ESLint (JavaScript) - FRONTEND

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

---

## 📘 Referencia 
📄 [PEP 8 — Style Guide for Python Code](doc\estilo-de-codigo\estilo-python-pep-8.pdf)

---



