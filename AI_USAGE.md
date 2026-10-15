# Uso de inteligencia artificial durante el desarrollo

Para este ejercicio he utilizado **OpenAI Codex** como herramienta de apoyo al
desarrollo.

El objetivo no ha sido delegar el ejercicio completo en la IA, sino utilizarla
como asistente dentro de un proceso en el que el alcance, las decisiones
principales y la aceptación final de los cambios permaneciesen bajo control
humano.

No se ha utilizado inteligencia artificial dentro de la propia aplicación.

El problema planteado consiste en operaciones deterministas de creación,
consulta y modificación de órdenes, por lo que no consideré que incorporar un
modelo de IA al producto aportase valor al usuario.

## Preparación antes de implementar

Antes de solicitar código a Codex se definieron dos documentos.

### `SPEC.md`

Contiene:

- objetivo del producto;
- funcionalidades requeridas;
- modelo de datos;
- límites de validación;
- requisitos de privacidad;
- tecnologías previstas;
- funcionalidades fuera de alcance;
- criterios de aceptación.

### `AGENTS.md`

Contiene las instrucciones que debía respetar el agente durante el desarrollo.

Entre otras:

- mantener soluciones sencillas;
- no ampliar el alcance sin autorización;
- minimizar dependencias;
- validar siempre en el backend;
- utilizar exclusivamente datos sintéticos;
- no introducir datos personales;
- no introducir secretos;
- utilizar SQL parametrizado;
- ejecutar pruebas después de los cambios;
- no debilitar tests para conseguir que pasasen.

La intención fue proporcionar un contexto estable al agente antes de comenzar
la implementación.

## Flujo de trabajo utilizado

El proceso general seguido fue:

```text
Definir requisitos
        ↓
Solicitar una propuesta
        ↓
Revisar la propuesta
        ↓
Aprobar decisiones concretas
        ↓
Permitir la implementación
        ↓
Revisar el código generado
        ↓
Ejecutar las comprobaciones personalmente
        ↓
Aceptar o devolver cambios concretos
```

No se comenzó con una instrucción genérica para generar la aplicación completa.

## Primera interacción con Codex

Antes de permitir modificaciones, se pidió a Codex que leyese `SPEC.md` y
`AGENTS.md` y explicase:

- qué entendía que debía construir;
- qué restricciones existían;
- qué quedaba fuera de alcance;
- qué arquitectura de backend proponía.

La propuesta fue revisada antes de autorizar la implementación.

Se aprobaron explícitamente decisiones como:

- FastAPI;
- Pydantic;
- SQLite;
- módulo `sqlite3` de Python;
- ausencia de ORM;
- tres endpoints;
- estado inicial `pending`;
- validación estricta;
- rechazo de campos inesperados;
- consultas SQL parametrizadas;
- pruebas mediante bases SQLite temporales.

## Implementación del backend

Codex recibió una tarea limitada exclusivamente al backend y sus tests.

No tenía autorización para:

- implementar el frontend;
- modificar la especificación;
- introducir autenticación;
- introducir servicios cloud;
- añadir un ORM;
- añadir Docker en esa fase;
- realizar commits.

Al finalizar la tarea revisé manualmente:

- estructura de archivos;
- modelos de Pydantic;
- enum de estados;
- límites de campos;
- rechazo de campos adicionales;
- consultas SQLite;
- uso de parámetros SQL;
- apertura y cierre de conexiones;
- códigos HTTP;
- aislamiento de las bases de datos de pruebas;
- contenido de los tests.

## Un fallo detectado durante la verificación humana

Aunque la implementación inicial había sido presentada como terminada, al
ejecutar personalmente:

```sh
pytest -v
```

desde la raíz del repositorio, la colección de tests falló con:

```text
ModuleNotFoundError: No module named 'backend'
```

Esto confirmó que no era suficiente con aceptar que el agente indicase que sus
comprobaciones habían funcionado.

El problema se reprodujo de forma independiente y se devolvió a Codex como una
tarea muy concreta:

- corregir únicamente la configuración de importación de pytest;
- no modificar el comportamiento de la aplicación;
- no introducir manipulación de `sys.path` dentro de los tests;
- no realizar cambios no relacionados.

La solución añadida fue:

```ini
[pytest]
pythonpath = .
```

Después volví a ejecutar personalmente la suite completa y comprobé que los
tests se recogían y ejecutaban correctamente.

## Implementación del frontend

Una vez aceptado el backend, se solicitó la implementación del frontend como
una tarea separada.

Se indicaron restricciones como:

- React;
- TypeScript;
- Vite;
- interfaz en castellano;
- dependencias mínimas;
- sin librerías de componentes;
- sin gestor global de estado;
- sin persistencia mediante `localStorage`;
- sin campos de información personal;
- utilización exacta de la API existente.

También se autorizó únicamente la configuración CORS mínima necesaria para la
integración local.

Después de la implementación revisé manualmente:

- tipos de TypeScript;
- cliente de API;
- campos del formulario;
- tratamiento de errores;
- estados de carga;
- comportamiento ante peticiones fallidas;
- ausencia de datos personales adicionales;
- ausencia de almacenamiento local;
- configuración de Vite;
- configuración CORS;
- interfaz y estilos.

Posteriormente ejecuté las comprobaciones de TypeScript y build y probé
manualmente el flujo completo en el navegador.

## Docker

Docker se incorporó posteriormente como una tarea separada y explícitamente
autorizada.

La instrucción pedía mantenerlo como una ayuda para reproducir el entorno local,
sin cambiar la arquitectura de la aplicación.

Durante la revisión se comprobaron, entre otros aspectos:

- Dockerfiles de backend y frontend;
- imágenes base utilizadas;
- usuarios dentro de los contenedores;
- publicación de puertos;
- persistencia SQLite;
- volumen Docker;
- configuración mediante variable de entorno;
- `.dockerignore`;
- ausencia de secretos;
- ausencia de montajes innecesarios del host.

Los servicios se publican únicamente en:

```text
127.0.0.1:8000
127.0.0.1:5173
```

Los procesos de aplicación dentro de los contenedores se ejecutan con usuarios
no root.

También se comprobó que una reparación permaneciese disponible después de
recrear los contenedores utilizando el mismo volumen persistente.

## Comprobaciones realizadas independientemente

La salida generada por IA se trató como una propuesta y no como un resultado
confiable por defecto.

Entre las verificaciones realizadas personalmente se encuentran:

- revisión de diffs;
- comparación con la especificación;
- revisión manual del código;
- ejecución independiente de pytest;
- pruebas con datos inválidos;
- pruebas con campos inesperados;
- prueba con texto similar a una inyección SQL;
- revisión del SQL parametrizado;
- comprobación de persistencia tras reiniciar la aplicación;
- pruebas manuales mediante Swagger;
- pruebas manuales en navegador;
- simulación de errores de comunicación con el backend;
- comprobación de TypeScript;
- build del frontend;
- comprobación de Docker Compose;
- construcción de las imágenes;
- ejecución de los contenedores;
- comprobación de persistencia después de recrearlos.

La suite final contiene **87 pruebas automatizadas**.

## Revisión mediante una sesión separada

Después de completar backend, frontend e integración se abrió una nueva sesión
de Codex destinada exclusivamente a revisión.

Esta sesión no había participado en la implementación anterior.

Se le indicó expresamente:

- no modificar archivos;
- actuar únicamente como reviewer;
- comparar la implementación con `SPEC.md`;
- priorizar errores funcionales;
- revisar privacidad;
- revisar seguridad;
- revisar validación;
- revisar persistencia;
- revisar integración frontend/backend;
- diferenciar defectos de preferencias de estilo;
- no proponer funcionalidades nuevas.

La revisión no encontró defectos confirmados de funcionamiento, seguridad,
privacidad o persistencia en el código revisado.

Separar las sesiones no equivale a disponer de una segunda persona
independiente, puesto que se sigue utilizando la misma herramienta de IA, pero
permite separar el contexto y la responsabilidad de implementación de la tarea
de revisión.

## Privacidad durante el uso de IA

Durante el desarrollo se utilizaron únicamente datos sintéticos.

No se proporcionaron intencionadamente a Codex:

- nombres reales de clientes;
- números de teléfono reales;
- correos electrónicos reales;
- direcciones;
- datos de pago;
- contraseñas;
- tokens;
- claves API;
- credenciales.

Los datos utilizados en pruebas siguen formatos ficticios como:

```text
SYNTHETIC-001
CLI-001
```

También se evitó introducir secretos en el repositorio.

Archivos como bases de datos de ejecución, entornos virtuales, archivos `.env`,
logs, dependencias instaladas y artefactos de build están excluidos del control
de versiones cuando corresponde.

## Privacidad en el código generado

Los modelos de entrada no contienen campos específicos de información personal.

Además, están configurados para rechazar campos inesperados.

Esto se comprobó tanto mediante tests como manualmente.

Por ejemplo, un campo adicional como:

```text
phone
```

no se ignora ni se almacena, sino que provoca un error de validación.

También se revisó que la aplicación no registrase innecesariamente cuerpos
completos de peticiones ni descripciones de reparaciones.

## Criterio de aceptación de resultados de IA

Las propuestas de la IA no se aplicaron automáticamente.

El criterio utilizado fue aproximadamente:

```text
Defecto real
    → corregir

Decisión técnica necesaria
    → revisar y aprobar antes de implementar

Sugerencia razonable pero fuera de alcance
    → no incorporar

Preferencia de estilo
    → valorar, no aplicar automáticamente

Falso positivo
    → descartar
```

Este enfoque permitió utilizar la velocidad de la herramienta sin delegar en
ella la responsabilidad final sobre el resultado.

## Resumen

La IA se utilizó principalmente como:

```text
Asistente de implementación
        +
Generador de tests
        +
Herramienta de revisión
```

pero las decisiones principales siguieron este flujo:

```text
IA propone
    ↓
desarrollador revisa
    ↓
desarrollador comprueba
    ↓
desarrollador acepta o rechaza
```

El fallo de configuración de pytest encontrado durante la revisión manual fue
un ejemplo concreto de por qué consideré necesario mantener esa separación
durante todo el ejercicio.