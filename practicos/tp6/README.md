# README: Proyecto Inscripción de Actividades (TP6)

Este proyecto implementa la US "inscribirme a actividades" utilizando la metodología **TDD (Test-Driven Development)**, con **Python** y **Pytest**.

---

## 1. Configuración del IDE (Sources Root)

Este paso es **obligatorio y local** para que el IDE (PyCharm, VS Code) resuelva los *imports* (ej., `from back.src...`) sin errores de **`ImportError`**.

1. Haz clic derecho en la carpeta **`tp6`** y márcala como **"Sources Root"** (Raíz de Fuentes).

![img.png](doc/img.png)

---

## 2. Dependencias Requeridas

| Paquete | Instalación | Propósito |
| :--- | :--- | :--- |
| **`pytest`** | `pip install pytest` | Marco de trabajo para la ejecución de tests unitarios. |

---

## 3. Ejecución de Tests Unitarios

Asegúrate de que la terminal esté posicionada en la raíz del proyecto (carpeta `tp6`).

### Opción A: Ejecución Directa de Pytest

```bash
pytest -v back/tests/test_inscripcion.py
 ```
### Opción B: Ejecución como Módulo Python
Si la Opción A falla debido a problemas con el PATH, utiliza:

```bash
python -m pytest -v back/tests/test_inscripcion.py
 ```