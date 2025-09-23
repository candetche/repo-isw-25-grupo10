# Plan de gestión de configuración

### Ingeniería y calidad de software - Grupo 10

**2025**

**Enlace del repositorio:** https://github.com/candetche/repo-isw-25-grupo10

## Estructura del repositorio

```plaintext
repo-isw-25-grupo10
│── material-de-clases
|    │── bibliografia
|    └── presentaciones-clases
|    └── templates-para-practicos-y-parciales
│── README.md
│── planificacion
│
│── notas-de-clases
│
│── practicos
|    └── tp<N>
|        │── Consigna
|        └── Entrega
└── trabajos-investigacion-grupal
    └── tp<N>
        │── Consigna
        └── Presentacion
```

## Ítems de configuración

- Documentación del plan de gestión de configuración
- ReadMe.md
- Versiones de software
- Código fuente
- Notas de clases
- Consignas de trabajos practicos
- Entregas de trabajos practicos
- Presentacions de trabajos practicos
- Manual de instalación
- Bibliografia
- Presentaciones de clases
- Templates para practicos y parciales

## Reglas de Nombrado

**Archivos y carpetas:**
Nombres descriptivos en minúscula y palabras separadas por guión medio (-).

| Item de configuración | Regla de nombrado                 |
| --------------------- | ------------------------          |
| Notas de clase        | `fecha-u<N>.<extensión>`          |
| Consigna TP           | `consigna-tp<N>.<extensión> `     |
| Entrega TP            | `entrega-tp<N>.<extensión> `      |
| Presentacion TP       | `presentacion-tp<N>.<extensión> ` |
| Codigo fuente         | `nombre.<extensión>`               |
| Manual de instalación | `manual-TP<N>.md`                 |


**Convención de nombrado de commits:**
Los mensajes de commit deben seguir el siguiente formato:
`<prefijo>` - descripción breve

| Prefijo     | Descripción                                     | Ejemplo                                                   |
| ----------  | --------------------------------------------    | --------------------------------------------------------- |
| `bug-`   | Corrección de un bug (código).                  | bug-se corrige comportamiento en validación de login |
| `imp-`   | Mejoras o refactor de código (improvements).    | imp-optimización de consulta en base de datos        |
| `feat-`  | Nueva funcionalidad (feature).                  | feat-se agrega exportar reporte a PDF                |
| `doc-`   | Cambios en documentación.                       | doc-actualización readme.md                          |
| `misc-`  | Otros cambios menores (misceláneo).             | misc-se agregó un .gitkeep                           |
| `Rename <nombre-anterior> to <nombre-nuevo>`| Cambiar nombre a item de configuracion | Rename-Metodo-lean-startup to metodo-lean-startup|


## Branching

main: Rama principal estable.
dev/tp<N>: Una rama por trabajo práctico, donde se tengan los cambios aprobados por todos los integrantes. Luego esta rama será integrada a main y a la LB una vez aprobada. 
<tipo>/nombre-descriptivo-de-lo-que-vamos-a-hacer: ramas específicas según los cambios a realizar. Luego esta rama será integrada a su respectiva rama dev/tp<N> una vez aprobada.

## Herramientas a utilizar para SCM

- Github: Accesibilidad, más utilizado para proyectos open source (dijo profe), permite manejo de versionado, diferentes ramas y resolución de conflictos.
- Git: herramienta de línea de comandos para commits, ramas y merges.

## Criterio para linea base

Cada línea base será definida luego de la entrega de un trabajo práctico grupal. Consideramos que con la entrega el estado del proyecto ha sido revisado y validado por todos los integrantes del grupo.

Implementación: Uso de tags. git tag -a LB1 -m `LB<N>: <descripción>`

## Glosario

- `<N>`: número de ítem (1, 2, …)
- `<tp>`: trabajo práctico
- `<tpi>`: trabajo práctico de investigación
- `<extension>`: extensión del archivo (.pdf, .jpg, .py, …)
- `<mm-dd>`: fecha en el formato mm-dd en el que fue tomado el elemento
- `LB`: línea base
