# Auditoria de Sistemas Legacy: "Del Dato a la Decision"

## Eco-Distribuidora S.A. — Informe de Auditoria Tecnica

**Squad:** DS3

**Integrantes:**
- Snaider Brayan Quispe Janco
- Jonathan Smith Soraire Rojas
- Ana Paola Viscarra Chambi

**Fecha:** Junio 2026

---

## 1. Resumen Ejecutivo

Eco-Distribuidora S.A. cuenta con un sistema CRUD tradicional para la gestion de inventario y ventas. Si bien el sistema es funcional para operaciones basicas de registro, **no proporciona capacidades de soporte a la decision (DSS)**. La gerencia no puede responder preguntas criticas como "¿Que productos se agotaran en 15 dias?" o "¿Que clientes estan disminuyendo su frecuencia de compra?". Este informe identifica las fallas desde la Teoria General de Sistemas (TGS) y propone una hoja de ruta hacia un DSS.

---

## 2. Diagrama de la Base de Datos Actual (Reversa de Ingenieria)

```
+-------------------+          +-------------------+
|     Producto      |          |      Venta        |
+-------------------+          +-------------------+
| PK id: INTEGER    |          | PK id: INTEGER    |
| nombre: VARCHAR   |          | producto_id: INT  |
| categoria: VARCHAR|          | producto_nombre   |
| precio: FLOAT     |          | cantidad: INT     |
| stock: INTEGER    |          | precio_unitario   |
| proveedor: VARCHAR|          | total: FLOAT      |
+-------------------+          | fecha: VARCHAR    |
                                | cliente: VARCHAR  |
                                +-------------------+
```

**Problemas estructurales detectados:**
- **Sin clave foranea**: `Venta.producto_id` no tiene una restriccion FK real hacia `Producto.id`.
- **Duplicacion de datos**: `Venta.producto_nombre` y `Venta.precio_unitario` duplican informacion de la tabla Producto, generando riesgo de inconsistencia.
- **Fecha como texto**: La columna `fecha` es VARCHAR en lugar de DATE, impidiendo calculos temporales nativos.
- **Sin tabla Cliente**: El cliente es solo un campo de texto en Ventas, imposibilitando analisis de frecuencia por cliente.
- **Sin tabla Categoria/Proveedor**: Categoria y Proveedor son textos planos, no entidades normalizadas.

---

## 3. Analisis desde la Teoria General de Sistemas (TGS)

### 3.1 Entropia: Perdida de Orden de la Informacion

| Falla de Entropia | Descripcion | Impacto |
|---|---|---|
| **E1: Datos obsoletos sin depurar** | El sistema acumula productos con stock = 0 y ventas antiguas sin ningun mecanismo de archivado o purga. Con el tiempo, las tablas se llenan de registros irrelevantes que el usuario debe escanear manualmente. | El operador pierde tiempo buscando informacion relevante entre datos inservibles. La relacion senal/ruido disminuye progresivamente. |
| **E2: Inconsistencia por falta de relaciones** | Al no existir clave foranea real, si un producto se elimina, sus ventas historicas quedan huerfanas con un `producto_id` que ya no existe. El sistema no previene ni gestiona esta degradacion. | Los reportes generan numeros incorrectos, erosionando la confianza en los datos. |
| **E3: Fechas como texto** | Almacenar fechas como VARCHAR impide ordenar cronologicamente de forma nativa, calcular diferencias entre fechas o generar series temporales. La informacion temporal pierde su significado semantico. | Imposibilidad total de hacer analisis de tendencias o estacionalidad. |

### 3.2 Falta de Sinergia

**Problema:** La suma de las partes (tabla Productos + tabla Ventas) no genera valor superior. El sistema opera como dos silos aislados:

- **Productos** se actualiza independientemente de **Ventas**.
- No existe un calculo automatico de `stock - ventas` para pronosticar agotamiento.
- No se correlacionan categorias con volumen de ventas.
- No se identifican patrones de compra por cliente.

**Por que ocurre:** El CRUD fue disenado para la **captura de datos**, no para la **generacion de informacion**. Cada tabla resuelve una necesidad transaccional inmediata, pero ninguna vista consolida los datos en conocimiento util.

> "El todo deberia ser mayor que la suma de las partes, pero aqui el todo es igual a la suma de las partes, porque no existen mecanismos de integracion ni sintesis."

---

## 4. Analisis de Toma de Decisiones

### 3 Decisiones Criticas que el Sistema Actual NO Puede Soportar

| Decision Critica | Pregunta de Negocio | Por que el CRUD Fallo |
|---|---|---|
| **D1: Reabastecimiento predictivo** | "¿Que productos necesito reordenar en los proximos 15 dias?" | El sistema muestra stock actual pero no calcula ritmo de ventas diario ni proyecta fechas de agotamiento. Requiere que el usuario compare manualmente dos tablas. |
| **D2: Deteccion de clientes en riesgo** | "¿Que clientes estan comprando menos que el mes pasado?" | No existe una tabla Cliente con historial de compras. El campo "cliente" en Ventas es texto libre, imposibilitando cualquier agregacion por cliente. |
| **D3: Analisis de rentabilidad por categoria** | "¿Que categoria de producto genera mayor margen de contribucion?" | No hay relacion entre precio de costo (no registrado) y precio de venta. No hay calculos de margen, ROI por producto, ni rankings de rentabilidad. |

---

## 5. Cuadro Comparativo: CRUD Actual vs. DSS Necesario

| Dimension | CRUD Actual (Legacy) | DSS Necesario |
|---|---|---|
| **Proposito** | Registrar transacciones individuales | Soportar decisiones estrategicas |
| **Datos** | Planos, duplicados, sin relaciones | Normalizados, con claves foraneas y restricciones de integridad |
| **Temporalidad** | Solo estado actual (stock hoy) | Historico + Proyecciones futuras |
| **Alertas** | Ninguna | Alertas de stock bajo, clientes inactivos, tendencias negativas |
| **Visualizacion** | Tablas interminables sin paginacion | Dashboards con graficos, KPI cards, filtros interactivos |
| **Cliente** | Texto libre | Entidad Cliente con historial, segmentacion y scoring |
| **Analitica** | Cero. Solo SELECT * FROM tabla | Modelos predictivos, promedios moviles, tendencias |
| **Exportacion** | No disponible | Exportacion a PDF/Excel con informes ejecutivos |
| **Paginacion** | No | Si, con busqueda y filtros avanzados |

---

## 6. Propuesta de Evolucion: De CRUD a DSS

### 6.1 Nuevos Modulos Requeridos

1. **Modulo de Clientes**
   - Entidad Cliente con datos de contacto, segmentacion, frecuencia de compra.
   - Calculo automatico de RFM (Recencia, Frecuencia, Monto).

2. **Modulo de Alertas Predictivas**
   - Algoritmo que calcula ritmo de ventas diario (promedio movil de 7, 15, 30 dias).
   - Alerta cuando stock proyectado <= 0 en los proximos N dias.

3. **Modulo de Dashboard y Reporteria**
   - KPIs en tiempo real: "Dias hasta agotar stock", "Top 10 productos mas vendidos", "Clientes con baja frecuencia".
   - Graficos de tendencia semanal/mensual.

4. **Modulo de Gestion de Categorias y Proveedores**
   - Normalizar Categoria y Proveedor como tablas independientes.
   - Calculo de rentabilidad por categoria y evaluacion de proveedores.

### 6.2 KPIs Propuestos (Indicadores Clave de Desempeno)

| KPI | Formula | Frecuencia | Decisión que soporta |
|---|---|---|---|
| **KPI 1: Dias hasta agotar stock** | stock_actual / ventas_diarias_promedio_15d | Diaria | ¿Cuando reabastecer? |
| **KPI 2: Tasa de variacion de frecuencia de compra** | (compras_mes_actual / compras_mes_anterior - 1) * 100 | Mensual | ¿Que clientes estan migrando? |
| **KPI 3: Rotacion de inventario por categoria** | ventas_totales_categoria / stock_promedio_categoria | Semanal | ¿Que categorias tienen sobrestock? |

### 6.3 Diagramas UML Nuevos (Propuesta)

```
[Diagrama de Clases Propuesto]

+-------------------+       +-------------------+       +-------------------+
|      Cliente      |       |     Producto      |       |     Categoria     |
+-------------------+       +-------------------+       +-------------------+
| - id: int         |       | - id: int         |       | - id: int         |
| - nombre: string  |       | - nombre: string  |<>---->| - nombre: string  |
| - email: string   |       | - precio_costo    |       | - descripcion     |
| - telefono: string|       | - precio_venta    |       +-------------------+
| - segmento: string|       | - stock_minimo    |
| - fecha_registro  |       | - stock_actual    |       +-------------------+
+-------------------+       | - id_categoria    |       |    Proveedor      |
        |                   | - id_proveedor    |<>---->+-------------------+
        | 1                  +-------------------+       | - id: int         |
        |                         |                      | - nombre: string  |
        |                         | 1                    | - contacto        |
        |                         |                      | - telefono        |
        | 1                  +-------------------+       +-------------------+
        +--------------------|      Venta        |
                             +-------------------+
                             | - id: int         |
                             | - fecha: DATE     |
                             | - id_cliente: FK  |
                             | - id_producto: FK |
                             | - cantidad: int   |
                             | - precio_unitario |
                             | - total: float    |
                             +-------------------+
```

---

## 7. Conexion con ODS 8 (Trabajo Decente y Crecimiento Economico)

### ¿Como afecta la ineficiencia de este sistema al trabajador?

| Impacto Negativo | Descripcion |
|---|---|
| **Sobrecarga cognitiva** | El trabajador debe revisar tablas gigantes sin filtros para encontrar informacion relevante. Esto genera fatiga mental y disminuye la productividad. |
| **Decisiones intuitivas** | Al no contar con datos procesados, los empleados toman decisiones basadas en "corazonada" o experiencia, aumentando la probabilidad de error. |
| **Estrés por falta de herramientas** | La presion de "saber que falta algo pero no poder verlo en el sistema" genera ansiedad laboral y frustracion. |
| **Tiempo perdido en tareas manuales** | El trabajador dedica horas a cruzar datos entre tablas, tiempo que podria dedicarse a tareas de mayor valor estrategico. |

### Propuesta Etica (ODS 8.2)

Un DSS no solo mejora la rentabilidad: **mejora la calidad de vida laboral**. Automatizar la deteccion de tendencias y alertas libera al trabajador de tareas repetitivas y le permite enfocarse en juicio critico y accion estrategica. La tecnologia debe servir a la persona, no saturarla.

> "Un sistema que no ayuda a decidir no solo es inutil: es una carga para quien debe operarlo."

---

## 8. Conclusion

El sistema CRUD de Eco-Distribuidora S.A. cumple su funcion minima de registrar transacciones, pero **fracasa como herramienta de gestion**. Desde la TGS, observamos:

1. **Entropia creciente**: Los datos se degradan, duplican y desactualizan sin control.
2. **Falta de sinergia**: Las tablas no conversan entre si; la informacion estrategica no emerge.
3. **Nulo soporte decision**: 3 decisiones criticas de negocio no pueden responderse con el sistema actual.

La transformacion a un DSS requiere normalizar la base de datos, agregar capas de analitica predictiva y disenar interfaces centradas en la decision, no en la transaccion. Esto no solo hara mas rentable a la empresa, sino que mejorara las condiciones laborales de sus trabajadores (ODS 8).

---

## 9. Instrucciones de Ejecucion del Sistema Legacy

### Requisitos
- Python 3.8+
- pip

### Instalacion
```bash
pip install -r requirements.txt
```

### Ejecucion
```bash
python app.py
```

### Poblar la Base de Datos
```bash
sqlite3 instance/inventario.db < schema.sql
```

O ingresar manualmente los 50 productos desde la interfaz web en `http://localhost:5000/productos/nuevo`.

---

*Documento generado como parte de la Actividad 1: Auditoria de Sistemas Legacy - "Del Dato a la Decision"*

---

## Firmas del Squad

| Integrante | Firma Digital |
|---|---|
| Snaider Brayan Quispe Janco | `SnaiderSsj` |
| Integrante | Firma Digital |
|---|---|
| Ana paola viscarra | `pao024v` |

