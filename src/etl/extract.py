from pathlib import Path
import pandas as pd
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Resultado de una extraccion"""
    success: bool
    data: pd.DataFrame | None = None
    row_counts: int = 0
    error: str | None = None
    source: str = ""


def extract_csv(filepath: str | Path, encoding: str = "utf-8", delimiter: str = "," ) -> ExtractionResult:
    """
    Extrae datos de un archivo CSV.
    
    :param filepath: Description
    :type filepath: str | Path
    :param encoding: Description
    :type encoding: str
    :param delimiter: Description
    :type delimiter: str
    :return: Description
    :rtype: ExtractionResult
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        logger.error(f"Archivo no encontrado: {filepath}")
        return ExtractionResult(
            success=False,
            error=f"Archivo no encontrado: {filepath}",
            source=str(filepath)
        )
        
    try:
        logger.info(f"Extrayendo los datps de: {filepath}")
        try:
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter)
        except UnicodeDecodeError:
            logger.warning(f"Error de encoding, intentando latin-1")
            df = pd.read_csv(filepath, encoding="latin-1", delimiter=delimiter)

        logger.info(f"Extraidas {len(df)} filas, {len(df.columns)} columnas")
        
        return ExtractionResult(
            success=True,
            data=df,
            row_counts=len(df),
            source=str(filepath)
        )

    except Exception as e:
        logger.exception(f"Error extrayendo CSV: {e}")
        return ExtractionResult(
            success=False,
            error=str(e),
            source=str(filepath)
        )

def extract_from_supabase(table_name: str, filters: dict = None) -> ExtractionResult:
    """ Extrae datos desde una tabla Supabase"""
    from src.db.connection import get_supabase_client
    
    try:
        client = get_supabase_client()
        query = client.table(table_name).select("*")
        
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            logger.info(f"Extraidas {len(df)} filas de {table_name}")
            return ExtractionResult(
                success=True,
                data=df,
                row_counts=len(df),
                source=f"supabase: {table_name}"
            )
        else:
            return ExtractionResult(
                success=True,
                data=pd.DataFrame(),
                row_counts=0,
                source=f"supabase: {table_name}"
            )
    
    except Exception as e:
        logger.error(f"Error extrayendo de Supabase: {e}")
        return ExtractionResult(
            success=False,
            error=str(e),
            source=f"supabase: {table_name}"
        )
