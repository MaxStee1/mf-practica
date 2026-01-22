"""
Script principal para ejecutar el pipeline ETL.

Uso:
    uv run python scripts/run_etl.py data/raw/ventas_raw.csv
    uv run python scripts/run_etl.py data/raw/ventas_raw.csv --dry-run
"""
import argparse
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.pipeline import run_pipeline, setup_logging


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline ETL para datos de ventas"
    )
    parser.add_argument(
        "input_file",
        help="Ruta al archivo CSV de entrada"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar sin cargar a Supabase"
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directorio de salida (default: data/processed)"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_file = setup_logging()
    print(f"📝 Log file: {log_file}")
    
    # Ejecutar pipeline
    result = run_pipeline(
        input_file=args.input_file,
        dry_run=args.dry_run,
        output_dir=args.output_dir
    )
    
    # Exit code
    if result.success:
        print("\n✅ Pipeline completado exitosamente")
        sys.exit(0)
    else:
        print(f"\n❌ Pipeline falló: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
