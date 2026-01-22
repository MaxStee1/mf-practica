# Practica Profesional – Data Engineering con Python

Proyecto de práctica profesional enfocado en el desarrollo de un pipeline de datos usando Python, Supabase y buenas prácticas de ingeniería de datos.

## 🎯 Objetivo

Diseñar e implementar una arquitectura simple pero sólida que cubra:
- Acceso a datos mediante un Data Access Layer (DAL)
- Integración con Supabase como backend
- Construcción de un pipeline ETL (Extract, Transform, Load)
- Buenas prácticas de estructura, logging y versionado

## 🧱 Estructura del proyecto

```text
.
├── data/               # Datos de entrada, salida y logs
├── scripts/            # Scripts ejecutables
├── src/                # Código fuente
│   ├── config/         # Configuración y settings
│   ├── db/             # Capa de acceso a datos (DAL)
│   └── etl/            # Pipeline ETL
├── .env.example        # Variables de entorno de ejemplo
├── pyproject.toml
└── README.md
```

## 📘 Módulos del Proyecto

### 📦 Módulo 1 – Setup del Proyecto y Entorno

#### Resumen
- Inicialización del proyecto con **uv**
- Configuración de entorno virtual
- Definición de estructura base del proyecto
- Uso de variables de entorno mediante `.env`

#### Conceptos trabajados
- Gestión de dependencias
- Estructura de proyectos Python
- Buenas prácticas de configuración

---

### 📦 Módulo 2 – Supabase y Conexión Inicial

#### Resumen
- Creación del proyecto en **Supabase**
- Configuración de credenciales (`SUPABASE_URL`, `SUPABASE_KEY`)
- Verificación de conexión desde Python

#### Conceptos trabajados
- Supabase como backend (**PostgreSQL**)
- Seguridad básica con variables de entorno
- Conexiones externas desde Python

---

### 📦 Módulo 3 – Data Access Layer (DAL)

#### Resumen
- Implementación de una capa de acceso a datos usando el patrón **Repository**
- Cliente de Supabase implementado como **Singleton**
- CRUD completo para entidades **categorías** y **productos**
- Soporte para *soft delete* y manejo de stock
- Script de prueba para validar operaciones contra la base de datos

#### Componentes clave
- `connection.py`: cliente Supabase centralizado  
- `base.py`: repositorio abstracto  
- `categoria.py` y `producto.py`: lógica específica por entidad  
- `test_db.py`: validación funcional del DAL  

#### Conceptos trabajados
- Repository Pattern  
- Singleton Pattern  
- Clases abstractas en Python  
- Tipado y manejo de errores  
- Separación de responsabilidades  

---

### 📤 Módulo 4 – ETL Básico - Extracción, Transformación y Carga

#### Resumen
- Diseño e implementación de un pipeline ETL completo en Python
- Extracción de datos desde archivos CSV con manejo de errores y encodings
- Transformación de datos con limpieza, validación y enriquecimiento
- Carga de datos procesados a Supabase con soporte batch y dry-run
- Generación automática de archivos procesados, rechazados y logs del proceso

#### Componentes clave
- `extract.py`: lectura de CSV y extracción desde Supabase
- `transform.py`: limpieza de datos, validaciones, deduplicación y cálculo de métricas
- `load.py`: carga batch a Supabase y exportación a CSV
- `pipeline.py`: orquestación completa del flujo ETL con logging
- `run_etl.py`: script de ejecución con argumentos por consola

#### Conceptos trabajados
- ETL (Extract – Transform – Load)
- Data Quality y validación de datos
- Batch processing
- Logging profesional en Python
- Dry-run y ejecución segura
- Separación de responsabilidades por módulo

---

### 📊 Módulo 5: Análisis de Datos con Pandas y NumPy

Este módulo permite generar reportes completos de análisis de ventas a partir de datos procesados.

#### Funciones principales
- `generate_ventas_report(df)`: Genera un reporte en formato Markdown con:
  - Resumen ejecutivo
  - Ventas por tienda
  - Análisis temporal (mensual y por día de la semana)
  - Crecimiento de ventas
  - Top 10 productos y vendedores
  - Análisis Pareto (80/20)
  - Detección de anomalías (outliers)
  - Conclusiones automáticas

El reporte se guarda automáticamente en la carpeta `reports/` con un timestamp en el nombre del archivo.



## 🚀 Tecnologías Utilizadas
- Python **3.11+**
- Supabase (**PostgreSQL**)
- pandas
- uv
- Git
