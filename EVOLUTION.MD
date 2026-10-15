# Posible evolución hacia un producto real

El proyecto actual está deliberadamente limitado al alcance solicitado para el
ejercicio: crear reparaciones, consultarlas y modificar su estado.

Si el software pasase de ser un prototipo a utilizarse diariamente en un taller
de bicicletas, su evolución afectaría no solo al modelo de datos, sino también a
las funcionalidades, la arquitectura, la seguridad, la infraestructura, las
integraciones y la forma de operar el sistema.

La intención no sería implementar todas estas capacidades de una vez, sino
incorporarlas cuando apareciese una necesidad real.

## Flujo de reparación

Los tres estados actuales:

```text
Pendiente
En reparación
Terminada
```

son suficientes para el prototipo.

Un taller real podría necesitar un flujo más detallado:

```text
Recepcionada
    ↓
Pendiente de diagnóstico
    ↓
Presupuesto preparado
    ↓
Esperando aprobación
    ↓
En reparación
    ↓
Esperando repuesto
    ↓
Terminada
    ↓
Entregada
```

En ese momento dejaría de permitirse cualquier transición entre estados y se
definirían reglas de negocio explícitas.

Por ejemplo, una reparación no debería poder pasar a `Terminada` si todavía
tiene tareas obligatorias o repuestos pendientes.

También podría ser necesario registrar:

- fecha de entrada;
- fecha prevista;
- diagnóstico;
- tareas realizadas;
- piezas utilizadas;
- tiempo de mano de obra;
- observaciones internas;
- fecha de finalización;
- fecha de entrega.

## Usuarios, autenticación y permisos

El prototipo actual no necesita sistema de usuarios.

En un taller con varios trabajadores introduciría autenticación y autorización.

Los permisos dependerían de las responsabilidades de cada persona.

Por ejemplo:

### Recepción

Podría:

- registrar clientes;
- registrar bicicletas;
- crear órdenes;
- consultar datos de contacto;
- gestionar presupuestos;
- entregar reparaciones.

### Mecánico

Podría:

- consultar las reparaciones asignadas;
- consultar la información técnica necesaria;
- registrar diagnóstico;
- registrar tareas;
- registrar piezas;
- modificar estados.

No necesitaría necesariamente acceder a toda la información de contacto del
cliente.

### Responsable

Podría:

- consultar todas las reparaciones;
- gestionar usuarios;
- asignar trabajos;
- consultar incidencias;
- consultar métricas;
- configurar determinados aspectos del sistema.

Los permisos siempre se comprobarían en el backend y no únicamente ocultando
acciones en la interfaz.

## Evolución del dominio

El modelo actual contiene exclusivamente la información necesaria para el
ejercicio.

Un producto real podría separar progresivamente entidades como:

```text
Customer
Bicycle
RepairOrder
RepairTask
Quote
Product
InventoryMovement
Invoice
User
AuditEvent
```

Una estructura simplificada podría ser:

```text
Customer
    │
    └── Bicycle
            │
            └── RepairOrder
                    ├── RepairTask
                    ├── RepairPart
                    └── Quote
```

Esto permitiría que:

- un cliente tuviese varias bicicletas;
- una bicicleta acumulase un historial de reparaciones;
- una reparación tuviese varias tareas;
- una reparación consumiese varios repuestos;
- los datos del cliente no se duplicasen en cada orden.

La evolución del dominio se realizaría a partir de los procesos reales del
taller y no intentando anticipar desde el inicio todas las posibilidades.

## Persistencia

SQLite es apropiado para el prototipo porque proporciona persistencia sin
necesidad de infraestructura externa.

Con varios empleados trabajando simultáneamente y un modelo más amplio,
migraría probablemente a PostgreSQL.

Esto permitiría gestionar mejor:

- concurrencia;
- transacciones más complejas;
- índices;
- relaciones entre entidades;
- búsquedas;
- informes;
- copias de seguridad;
- crecimiento del volumen de datos.

También incorporaría un sistema de migraciones para evolucionar el esquema de
forma controlada.

## Arquitectura

No migraría directamente a microservicios.

Mantendría inicialmente una única aplicación desplegable, pero organizada en
módulos con responsabilidades claras:

```text
customers/
bicycles/
repairs/
inventory/
quotes/
billing/
notifications/
users/
```

Conceptualmente:

```text
Frontend
    ↓
API
    ↓
Casos de uso
    ↓
Reglas de negocio
    ↓
Persistencia
```

La separación en servicios independientes solo tendría sentido si apareciesen
necesidades reales como:

- escalado independiente;
- equipos diferentes trabajando sobre dominios separados;
- ciclos de despliegue diferentes;
- cargas de trabajo muy distintas;
- necesidad de aislamiento operativo.

Mientras esas necesidades no existiesen, un monolito modular sería más sencillo
de desarrollar, desplegar, probar y mantener.

## Lógica de negocio

A medida que aumentase la complejidad evitaría introducir reglas importantes
directamente en las rutas HTTP.

Por ejemplo, completar una reparación podría implicar:

```text
Solicitud de cambio de estado
        ↓
¿Usuario autorizado?
        ↓
¿Transición permitida?
        ↓
¿Tareas obligatorias terminadas?
        ↓
¿Repuestos pendientes?
        ↓
Actualizar reparación
        ↓
Registrar evento
```

Estas reglas deberían estar centralizadas y cubiertas por tests.

## Inventario y repuestos

Una evolución natural sería incorporar inventario.

Cada reparación podría registrar los materiales o piezas utilizados.

Por ejemplo:

- cámaras;
- cubiertas;
- cadenas;
- pastillas de freno;
- cables;
- discos;
- componentes;
- consumibles.

El sistema podría gestionar:

- stock actual;
- cantidades mínimas;
- entradas;
- salidas;
- piezas reservadas;
- proveedores;
- costes;
- pedidos pendientes.

Una reparación podría quedar automáticamente marcada como `Esperando repuesto`
si falta una pieza necesaria.

## Presupuestos

Determinadas reparaciones podrían requerir aprobación antes de comenzar.

El flujo podría ser:

```text
Diagnóstico
    ↓
Presupuesto
    ↓
Aprobación / rechazo
    ↓
Reparación
```

El presupuesto podría contener:

- tareas previstas;
- horas estimadas;
- piezas;
- precios;
- impuestos;
- total estimado.

La autorización del cliente debería registrarse de forma apropiada según el
canal utilizado.

## Facturación y pagos

La facturación se mantendría como un dominio separado de la propia reparación.

Una reparación terminada podría generar una factura o ticket con:

- mano de obra;
- repuestos;
- impuestos;
- descuentos;
- total.

Si fuese necesario aceptar pagos electrónicos, utilizaría un proveedor
especializado.

Evitaría almacenar directamente números de tarjeta u otra información sensible
de pago dentro de la aplicación.

## Comunicaciones

El sistema podría enviar comunicaciones asociadas a eventos como:

- presupuesto disponible;
- aprobación pendiente;
- reparación iniciada;
- reparación terminada;
- bicicleta preparada para recoger.

Estas comunicaciones podrían realizarse por:

- correo electrónico;
- SMS;
- otros canales configurados por el negocio.

Intentaría desacoplar las notificaciones de la operación principal.

Por ejemplo:

```text
RepairCompleted
        ↓
Servicio de notificaciones
        ↓
Email / SMS
```

Si el volumen lo justificase, el envío podría realizarse de forma asíncrona.

## Privacidad

La introducción de clientes reales cambiaría significativamente los requisitos
de la aplicación.

Separaría los datos personales de la información operativa siempre que fuese
posible.

Por ejemplo:

```text
Customer
    id
    name
    phone
    email

RepairOrder
    id
    customer_id
    ...
```

La reparación almacenaría una referencia interna en lugar de copiar los datos
de contacto.

Aplicaría el principio de mínimo privilegio.

Una persona encargada de reparar una bicicleta podría necesitar:

- bicicleta;
- problema;
- diagnóstico;
- tareas;
- estado.

pero no necesariamente:

- teléfono;
- correo electrónico;
- dirección.

## Seguridad

Un producto real necesitaría controles adicionales:

- autenticación;
- autorización;
- permisos por rol;
- gestión segura de contraseñas;
- HTTPS;
- gestión de secretos;
- políticas de sesión;
- protección frente a abuso;
- backups;
- control de accesos;
- auditoría.

Los secretos nunca deberían almacenarse en Git ni introducirse directamente en
las imágenes Docker.

Dependiendo del entorno podrían almacenarse mediante variables protegidas o un
gestor de secretos.

## Auditoría y trazabilidad

Con varios usuarios sería importante saber:

- quién creó una orden;
- quién cambió su estado;
- cuándo se realizó el cambio;
- quién modificó un presupuesto;
- quién registró una pieza;
- quién marcó una bicicleta como entregada.

Podría mantenerse un historial de eventos:

```text
RepairCreated
DiagnosisAdded
QuoteCreated
QuoteApproved
RepairStarted
PartAdded
RepairCompleted
BicycleDelivered
```

Esto permitiría investigar incidencias y reconstruir el historial de una
reparación.

La auditoría debería evitar almacenar más información personal de la realmente
necesaria.

## Configuración por entornos

La configuración dejaría de estar directamente asociada al entorno local.

Variables como:

```text
DATABASE_URL
ALLOWED_ORIGINS
API_BASE_URL
LOG_LEVEL
```

se definirían por entorno.

Existirían configuraciones diferenciadas para:

```text
development
testing
staging
production
```

Los secretos se administrarían independientemente de la configuración pública.

## Frontend

Con más órdenes y usuarios, la interfaz también tendría que evolucionar.

Podrían incorporarse:

- búsqueda;
- filtros;
- ordenación;
- paginación;
- reparaciones asignadas;
- prioridades;
- indicadores de retrasos;
- historial de una bicicleta;
- vista de trabajo de cada mecánico;
- panel de recepción.

La información mostrada dependería también del rol del usuario.

Intentaría mantener la interfaz centrada en las tareas que realmente realiza
cada perfil, evitando mostrar información innecesaria.

## Despliegue

Docker seguiría siendo útil para conseguir entornos reproducibles.

Sin embargo, la configuración Docker actual está orientada al desarrollo local.

En producción no utilizaría Vite como servidor frontend.

El frontend se compilaría y se serviría como contenido estático mediante una
solución apropiada.

Una arquitectura inicial podría ser:

```text
Browser
    ↓
Frontend
    ↓
API
    ↓
PostgreSQL
```

y posteriormente incorporar servicios externos solo cuando fueran necesarios:

```text
                 ┌── Email / SMS
                 │
Frontend ── API ─┼── PostgreSQL
                 │
                 ├── Object storage
                 │
                 └── External services
```

## Observabilidad

En un producto utilizado diariamente sería necesario detectar problemas de
forma proactiva.

Añadiría progresivamente:

- logs estructurados;
- métricas;
- health checks;
- seguimiento de errores;
- alertas;
- tiempos de respuesta;
- identificadores de petición;
- monitorización de base de datos.

Evitaría registrar cuerpos completos de peticiones o información personal salvo
que existiese una necesidad concreta y justificada.

## Testing

A medida que creciese la aplicación ampliaría la estrategia de pruebas.

Podría incluir:

```text
Tests unitarios
        ↓
Tests de integración
        ↓
Tests de API
        ↓
Tests de frontend
        ↓
Tests end-to-end
```

Un flujo completo como:

```text
Crear reparación
    ↓
Diagnosticar
    ↓
Preparar presupuesto
    ↓
Aprobar
    ↓
Reparar
    ↓
Entregar
```

podría convertirse en una prueba end-to-end automatizada.

## Integración continua

Con un equipo trabajando de forma habitual añadiría un pipeline de CI.

Por ejemplo:

```text
Cambio de código
      ↓
Lint
      ↓
Typecheck
      ↓
Tests
      ↓
Build
      ↓
Comprobaciones de seguridad
      ↓
Integración
```

Los cambios no deberían integrarse si alguna de las comprobaciones necesarias
fallase.

## Despliegue continuo

Los despliegues deberían ser:

- reproducibles;
- automatizados;
- trazables;
- reversibles.

Sería importante poder identificar qué versión está desplegada y volver a una
versión anterior si aparece un problema.

## Escalabilidad

No diseñaría inicialmente el sistema para una escala muy superior a la que
realmente necesita un taller.

Comenzaría con:

```text
Frontend
    ↓
Backend modular
    ↓
PostgreSQL
```

y mediría el comportamiento real.

Solo introduciría elementos como:

- caché;
- colas;
- workers;
- procesamiento asíncrono;
- réplicas;
- servicios independientes;

cuando hubiese una necesidad observable.

Por ejemplo, el envío de notificaciones podría trasladarse a una cola si
comenzase a ralentizar las operaciones principales.

## Integraciones externas

En función del negocio podrían aparecer integraciones con:

- proveedores;
- servicios de facturación;
- plataformas de pago;
- correo electrónico;
- SMS;
- contabilidad;
- comercio electrónico.

Intentaría aislar cada integración detrás de una interfaz propia.

De esta forma, las reglas principales de reparación no quedarían acopladas a un
proveedor externo concreto.

## Evolución incremental

Intentaría evolucionar el software en pequeñas etapas.

Un posible orden sería:

1. clientes y bicicletas;
2. usuarios, autenticación y roles;
3. historial y flujo completo de reparación;
4. presupuestos y aprobación;
5. inventario y repuestos;
6. facturación;
7. comunicaciones;
8. auditoría;
9. migración de SQLite a PostgreSQL;
10. configuración por entornos;
11. integración continua;
12. observabilidad y despliegue de producción.

Este orden no sería fijo.

Las prioridades deberían depender de cómo se utilizase realmente la aplicación
y de qué problemas aportasen más valor resolver.

La arquitectura debería crecer a partir de esas necesidades y no únicamente de
las posibilidades técnicas.