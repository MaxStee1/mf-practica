import logging
from dataclasses import dataclass
import pandas as pd
from src.db.connection import get_supabase_client

logger = logging.getLogger(__name__)

@dataclass
class LoadResult:
    """Resultado de una carga."""
    success: bool
    rows_loaded: int = 0
    rows_failed: int = 0
    error: str | None = None


def load_to_supabase(
    df: pd.DataFrame,
    table_name: str,
    batch_size: int = 100,
    upsert: bool = False,
    conflict_columns: list = None,
) -> LoadResult:
    """
    Carga un DataFrame a Supabase.
    
    Args:
        df: DataFrame a cargar
        table_name: Nombre de la tabla destino
        batch_size: Tamaño del batch para insercion
        upsert: Si True, actualiza registros existentes
        conflict_columns: Columnas para detectar conflictos en upsert
    
    Returns:
        LoadResult con estadisticas
    """
    if df is None or df.empty:
        logger.warning("DataFrame vacio, nada que cargar")
        return LoadResult(success=True, rows_loaded=0)
    
    client = get_supabase_client()
    total_rows = len(df)
    rows_loaded = 0
    rows_failed = 0
    
    logger.info(f"Iniciando carga de {total_rows} filas a {table_name}")
    
    # Convertir DataFrame a lista de diccionarios
    records = df.to_dict('records')
    
    # Limpiar NaN y convertir tipos
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, (pd.Timestamp,)):
                record[key] = value.isoformat()
    
    # Cargar en batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        try:
            if upsert and conflict_columns:
                response = (
                    client
                    .table(table_name)
                    .upsert(batch, on_conflict=",".join(conflict_columns))
                    .execute()
                )
            else:
                response = (
                    client
                    .table(table_name)
                    .insert(batch)
                    .execute()
                )
            
            rows_loaded += len(batch)
            logger.debug(f"Batch {batch_num}: {len(batch)} filas cargadas")
            
        except Exception as e:
            rows_failed += len(batch)
            logger.error(f"Error en batch {batch_num}: {e}")
    
    success = rows_failed == 0
    logger.info(
        f"Carga completada: {rows_loaded} exitosas, {rows_failed} fallidas"
    )
    
    return LoadResult(
        success=success,
        rows_loaded=rows_loaded,
        rows_failed=rows_failed,
        error=None if success else f"{rows_failed} filas fallaron"
    )


def load_to_csv(
    df: pd.DataFrame,
    filepath: str,
    encoding: str = "utf-8",
) -> LoadResult:
    """
    Guarda un DataFrame a CSV (para datos procesados o rechazados).
    """
    try:
        df.to_csv(filepath, index=False, encoding=encoding)
        logger.info(f"Guardado CSV: {filepath} ({len(df)} filas)")
        return LoadResult(success=True, rows_loaded=len(df))
    except Exception as e:
        logger.error(f"Error guardando CSV: {e}")
        return LoadResult(success=False, error=str(e))
