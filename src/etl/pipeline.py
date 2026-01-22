"""
Orquestador del pipeline ETL.
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.etl.extract import extract_csv, extract_from_supabase, ExtractionResult
from src.etl.transform import transform_ventas, TransformResult
from src.etl.load import load_to_supabase, load_to_csv, LoadResult

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Resultado completo del pipeline."""
    success: bool
    extraction: ExtractionResult | None = None
    transformation: TransformResult | None = None
    load: LoadResult | None = None
    duration_seconds: float = 0
    error: str | None = None


def setup_logging(log_dir: str = "data/logs"):
    """Configura logging para el pipeline."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"etl_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file


def run_pipeline(
    input_file: str,
    dry_run: bool = False,
    output_dir: str = "data/processed",
) -> PipelineResult:
    """
    Ejecuta el pipeline ETL completo.
    
    Args:
        input_file: Ruta al archivo CSV de entrada
        dry_run: Si True, no carga a Supabase
        output_dir: Directorio para archivos de salida
    
    Returns:
        PipelineResult con resultados de cada etapa
    """
    start_time = datetime.now()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE ETL")
    logger.info(f"Input: {input_file}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("=" * 60)
    
    # ============ EXTRACT ============
    logger.info("\nFASE 1: EXTRACCION")
    extraction = extract_csv(input_file)
    
    if not extraction.success:
        return PipelineResult(
            success=False,
            extraction=extraction,
            error=f"Error en extraccion: {extraction.error}",
            duration_seconds=(datetime.now() - start_time).total_seconds()
        )
    
    # Obtener mapeo de productos desde Supabase
    logger.info("Obteniendo mapeo de productos...")
    productos_result = extract_from_supabase("productos")
    if not productos_result.success:
        return PipelineResult(
            success=False,
            extraction=extraction,
            error=f"Error obteniendo productos: {productos_result.error}",
            duration_seconds=(datetime.now() - start_time).total_seconds()
        )
    
    # Crear mapeo nombre -> id
    productos_map = {
        row['nombre']: row['id'] 
        for _, row in productos_result.data.iterrows()
    }
    logger.info(f"Productos mapeados: {len(productos_map)}")
    
    # ============ TRANSFORM ============
    logger.info("\nFASE 2: TRANSFORMACIoN")
    transformation = transform_ventas(extraction.data, productos_map)
    
    if not transformation.succes:
        return PipelineResult(
            succes=False,
            extraction=extraction,
            transformation=transformation,
            error=f"Error en transformacion: {transformation.error}",
            duration_seconds=(datetime.now() - start_time).total_seconds()
        )
    
    # Guardar datos procesados a CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    processed_file = Path(output_dir) / f"ventas_clean_{timestamp}.csv"
    load_to_csv(transformation.data, str(processed_file))
    
    # Guardar rechazados si hay
    if transformation.rejected_data is not None and len(transformation.rejected_data) > 0:
        rejected_file = Path(output_dir) / f"ventas_rejected_{timestamp}.csv"
        load_to_csv(transformation.rejected_data, str(rejected_file))
        logger.info(f"Rechazados guardados en: {rejected_file}")
    
    # ============ LOAD ============
    logger.info("\nFASE 3: CARGA")
    
    if dry_run:
        logger.info("DRY RUN - No se cargaran datos a Supabase")
        load_result = LoadResult(success=True, rows_loaded=0)
    else:
        load_result = load_to_supabase(
            transformation.data,
            table_name="ventas",
            batch_size=50
        )
    
    # ============ RESUMEN ============
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DEL PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Filas extraidas:      {extraction.row_counts}")
    logger.info(f"Filas transformadas:  {transformation.rows_output}")
    logger.info(f"Filas rechazadas:     {transformation.rows_rejected}")
    logger.info(f"Filas cargadas:       {load_result.rows_loaded}")
    logger.info(f"Duracion:             {duration:.2f} segundos")
    logger.info("=" * 60)
    
    return PipelineResult(
        success=True,
        extraction=extraction,
        transformation=transformation,
        load=load_result,
        duration_seconds=duration
    )
