"""
Script para generar todas las visualizaciones.

Uso:
    uv run python scripts/generate_charts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.db.connection import get_supabase_client
from src.visualization.config import setup_style, CHARTS_DIR
from src.visualization.charts import (
    plot_ventas_temporales,
    plot_barras_categoria,
    plot_distribucion_pie,
    plot_histograma_tickets,
    plot_boxplot_categorias,
    plot_heatmap_ventas,
    plot_tendencia_con_prediccion
)
from src.visualization.dashboard import generate_dashboard


def extraer_datos() -> pd.DataFrame:
    """Extrae datos de ventas con joins."""
    client = get_supabase_client()
    
    response = client.table('ventas').select(
        '*, productos(nombre, categorias(nombre))'
    ).execute()
    
    if not response.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(response.data)
    
    # Aplanar datos anidados
    df['producto'] = df['productos'].apply(
        lambda x: x.get('nombre') if x else 'Desconocido'
    )
    df['categoria'] = df['productos'].apply(
        lambda x: x.get('categorias', {}).get('nombre') if x else 'Sin categoría'
    )
    df = df.drop(columns=['productos'])
    
    return df


def main():
    print("=" * 60)
    print("📊 GENERACIÓN DE VISUALIZACIONES")
    print("=" * 60)
    
    # Configurar estilo
    setup_style()
    
    # Extraer datos
    print("\n📥 Extrayendo datos...")
    df = extraer_datos()
    
    if df.empty:
        print("❌ No hay datos para visualizar")
        return
    
    print(f"✅ {len(df)} registros extraídos")
    
    # Crear directorio de salida
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generar gráficos individuales
    print("\n📈 Generando gráficos...")
    
    # 1. Temporal
    print("  → Ventas temporales...")
    plot_ventas_temporales(df, save_path="ventas_temporales.png")
    
    # 2. Por categoría
    print("  → Barras por categoría...")
    plot_barras_categoria(df, save_path="ventas_categoria.png")
    
    # 3. Distribución tiendas
    print("  → Pie de tiendas...")
    plot_distribucion_pie(df, save_path="distribucion_tiendas.png")
    
    # 4. Histograma
    print("  → Histograma de tickets...")
    plot_histograma_tickets(df, save_path="histograma_tickets.png")
    
    # 5. Boxplot
    print("  → Boxplot por categoría...")
    plot_boxplot_categorias(df, save_path="boxplot_categorias.png")
    
    # 6. Heatmap
    print("  → Heatmap de ventas...")
    plot_heatmap_ventas(df, save_path="heatmap_ventas.png")
    
    # 7. Tendencia
    print("  → Tendencia con regresión...")
    plot_tendencia_con_prediccion(df, save_path="tendencia_ventas.png")
    
    # Dashboard
    print("\n📊 Generando dashboard...")
    generate_dashboard(df, save_path="dashboard_ventas.png")
    
    print("\n" + "=" * 60)
    print(f"✅ Gráficos guardados en: {CHARTS_DIR}")
    print("=" * 60)
    
    # Listar archivos generados
    print("\nArchivos generados:")
    for f in sorted(CHARTS_DIR.glob("*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"  📄 {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()