import logging
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from datetime import datetime


logger = logging.getLogger(__name__)

@dataclass
class TransformResult:
    """Resultado de una transformacion."""
    succes: bool
    data: pd.DataFrame | None = None
    rows_input: int = 0
    rows_output: int = 0
    rows_rejected: int = 0
    rejected_data: pd.DataFrame | None = None
    stats: dict = field(default_factory=dict)
    error: str | None = None

def parse_date_flexible(date_str: str) -> datetime | None:
    """Intenta parsear una fecha en multiples formatos."""
    if pd.isna(date_str) or date_str == "":
        return None
    

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError:
            continue
    
    return None


def clean_string(value: str) -> str:
    """Limpia un string: trim y normaliza espacios."""
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def transform_ventas(df: pd.DataFrame, productos_map: dict) -> TransformResult:
    """
    Transforma datos de ventas crudos.
    
    Args:
        df: DataFrame con datos crudos
        productos_map: Dict {nombre_producto: id} para mapeo
    
    Returns:
        TransformResult con datos limpios
    """
    if df is None or df.empty:
        return TransformResult(
            success=False,
            error="DataFrame vacio o nulo"
        )
    
    rows_input = len(df)
    logger.info(f"Iniciando transformacion de {rows_input} filas")
    
    # Crear copia para no modificar original
    df_work = df.copy()
    
    # Track de rechazados
    rejected_rows = []
    rejection_reasons = []
    
    # 1. Limpiar strings
    logger.info("Limpiando strings...")
    if 'producto' in df_work.columns:
        df_work['producto'] = df_work['producto'].apply(clean_string)
    if 'tienda' in df_work.columns:
        df_work['tienda'] = df_work['tienda'].apply(clean_string)
    if 'vendedor' in df_work.columns:
        df_work['vendedor'] = df_work['vendedor'].apply(clean_string)
    
    # 2. Parsear fechas
    logger.info("Parseando fechas...")
    df_work['fecha_parsed'] = df_work['fecha'].apply(parse_date_flexible)
    
    # Rechazar filas con fecha invalida
    mask_fecha_invalida = df_work['fecha_parsed'].isna()
    if mask_fecha_invalida.any():
        rejected_rows.extend(df_work[mask_fecha_invalida].index.tolist())
        rejection_reasons.extend(['fecha_invalida'] * mask_fecha_invalida.sum())
        logger.warning(f"Fechas invalidas: {mask_fecha_invalida.sum()}")
    
    # 3. Convertir tipos numericos
    logger.info("Convirtiendo tipos numericos...")
    df_work['cantidad'] = pd.to_numeric(df_work['cantidad'], errors='coerce')
    df_work['precio_unitario'] = pd.to_numeric(df_work['precio_unitario'], errors='coerce')
    
    # 4. Validar rangos
    mask_cantidad_invalida = (df_work['cantidad'].isna()) | (df_work['cantidad'] <= 0)
    mask_precio_invalido = (df_work['precio_unitario'].isna()) | (df_work['precio_unitario'] <= 0)
    
    if mask_cantidad_invalida.any():
        nuevos_rechazos = df_work[mask_cantidad_invalida].index.tolist()
        rejected_rows.extend(nuevos_rechazos)
        rejection_reasons.extend(['cantidad_invalida'] * len(nuevos_rechazos))
        logger.warning(f"Cantidades invalidas: {mask_cantidad_invalida.sum()}")
    
    if mask_precio_invalido.any():
        nuevos_rechazos = df_work[mask_precio_invalido].index.tolist()
        rejected_rows.extend(nuevos_rechazos)
        rejection_reasons.extend(['precio_invalido'] * len(nuevos_rechazos))
        logger.warning(f"Precios invalidos: {mask_precio_invalido.sum()}")
    
    # 5. Mapear productos a IDs
    logger.info("Mapeando productos a IDs...")
    # Normalizar nombres para matching
    productos_map_lower = {k.lower().strip(): v for k, v in productos_map.items()}
    
    def map_producto(nombre: str) -> int | None:
        if pd.isna(nombre):
            return None
        nombre_norm = nombre.lower().strip()
        return productos_map_lower.get(nombre_norm)
    
    df_work['producto_id'] = df_work['producto'].apply(map_producto)
    
    mask_producto_no_encontrado = df_work['producto_id'].isna()
    if mask_producto_no_encontrado.any():
        nuevos_rechazos = df_work[mask_producto_no_encontrado].index.tolist()
        rejected_rows.extend(nuevos_rechazos)
        rejection_reasons.extend(['producto_no_encontrado'] * len(nuevos_rechazos))
        logger.warning(f"Productos no mapeados: {mask_producto_no_encontrado.sum()}")
    
    # 6. Eliminar duplicados
    logger.info("Eliminando duplicados...")
    cols_dedup = ['fecha', 'producto', 'cantidad', 'precio_unitario', 'tienda']
    cols_existentes = [c for c in cols_dedup if c in df_work.columns]
    duplicados_antes = len(df_work)
    df_work = df_work.drop_duplicates(subset=cols_existentes, keep='first')
    duplicados_eliminados = duplicados_antes - len(df_work)
    logger.info(f"Duplicados eliminados: {duplicados_eliminados}")
    
    # 7. Filtrar filas validas
    all_rejected = list(set(rejected_rows))
    df_rejected = df.loc[df.index.isin(all_rejected)].copy()
    df_clean = df_work.loc[~df_work.index.isin(all_rejected)].copy()
    
    # 8. Calcular total
    df_clean['total'] = df_clean['cantidad'] * df_clean['precio_unitario']
    
    # 9. Formatear fecha final
    df_clean['fecha'] = df_clean['fecha_parsed'].dt.strftime('%Y-%m-%d')
    
    # 10. Seleccionar columnas finales
    columnas_finales = [
        'fecha', 'producto_id', 'cantidad', 
        'precio_unitario', 'total', 'tienda', 'vendedor'
    ]
    df_output = df_clean[columnas_finales].copy()
    
    # Estadisticas
    stats = {
        'fechas_invalidas': int(mask_fecha_invalida.sum()),
        'cantidades_invalidas': int(mask_cantidad_invalida.sum()),
        'precios_invalidos': int(mask_precio_invalido.sum()),
        'productos_no_mapeados': int(mask_producto_no_encontrado.sum()),
        'duplicados_eliminados': duplicados_eliminados,
    }
    
    logger.info(f"Transformacion completada: {len(df_output)} filas validas")
    
    return TransformResult(
        succes=True,
        data=df_output,
        rows_input=rows_input,
        rows_output=len(df_output),
        rows_rejected=len(df_rejected),
        rejected_data=df_rejected,
        stats=stats
    )