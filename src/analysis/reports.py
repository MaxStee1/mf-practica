"""
Módulo de generación de reportes.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any

from src.analysis.exploratory import (
    describe_dataframe, 
    get_numeric_summary,
    check_missing_values
)
from src.analysis.aggregations import (
    ventas_por_categoria,
    ventas_por_periodo,
    ranking_productos,
    ranking_vendedores,
    ventas_por_tienda,
    analisis_dia_semana
)
from src.analysis.metrics import (
    calcular_ticket_promedio,
    calcular_unidades_promedio,
    calcular_crecimiento,
    identificar_outliers,
    calcular_pareto
)


def df_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Convierte DataFrame a tabla Markdown."""
    if len(df) > max_rows:
        df = df.head(max_rows)
    return df.to_markdown(index=False)


def generate_ventas_report(
    df: pd.DataFrame,
    output_dir: str = "reports"
) -> str:
    """
    Genera reporte completo de análisis de ventas.
    
    Args:
        df: DataFrame con datos de ventas
        output_dir: Directorio de salida
    
    Returns:
        Ruta al archivo generado
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(output_dir) / f"ventas_report_{timestamp}.md"
    
    # Comenzar reporte
    lines = []
    lines.append("# 📊 Reporte de Análisis de Ventas")
    lines.append(f"\n**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n**Registros analizados:** {len(df):,}")
    
    # ========== RESUMEN EJECUTIVO ==========
    lines.append("\n---\n## 📋 Resumen Ejecutivo\n")
    
    ticket_promedio = calcular_ticket_promedio(df)
    unidades_promedio = calcular_unidades_promedio(df)
    venta_total = df['total'].sum()
    
    lines.append(f"| Métrica | Valor |")
    lines.append(f"|---------|-------|")
    lines.append(f"| Venta Total | ${venta_total:,.2f} |")
    lines.append(f"| Ticket Promedio | ${ticket_promedio:,.2f} |")
    lines.append(f"| Unidades Promedio | {unidades_promedio:.1f} |")
    lines.append(f"| Total Transacciones | {len(df):,} |")
    
    # ========== ANÁLISIS POR TIENDA ==========
    lines.append("\n---\n## 🏪 Ventas por Tienda\n")
    tiendas = ventas_por_tienda(df)
    lines.append(df_to_markdown(tiendas))
    
    # ========== ANÁLISIS TEMPORAL ==========
    lines.append("\n---\n## 📅 Análisis Temporal\n")
    
    # Por mes
    lines.append("\n### Ventas Mensuales\n")
    mensual = ventas_por_periodo(df, periodo='ME')
    lines.append(df_to_markdown(mensual))
    
    # Por día de semana
    lines.append("\n### Ventas por Día de la Semana\n")
    dias = analisis_dia_semana(df)
    lines.append(df_to_markdown(dias))
    
    # Crecimiento
    lines.append("\n### Crecimiento Mensual\n")
    crecimiento = calcular_crecimiento(df, periodo='ME')
    lines.append(df_to_markdown(crecimiento.dropna()))
    
    # ========== TOP PRODUCTOS ==========
    lines.append("\n---\n## 🏆 Top 10 Productos\n")
    top_productos = ranking_productos(df, top_n=10)
    lines.append(df_to_markdown(top_productos))
    
    # ========== TOP VENDEDORES ==========
    lines.append("\n---\n## 👤 Top 10 Vendedores\n")
    top_vendedores = ranking_vendedores(df, top_n=10)
    lines.append(df_to_markdown(top_vendedores))
    
    # ========== ANÁLISIS PARETO ==========
    lines.append("\n---\n## 📈 Análisis Pareto (80/20)\n")
    pareto = calcular_pareto(df)
    stats = pareto.attrs.get('pareto_stats', {})
    
    lines.append(f"\n**Hallazgo:** El {stats.get('pct_items_80_valor', 'N/A')}% de los productos ")
    lines.append(f"({stats.get('items_80_pct_valor', 'N/A')} de {stats.get('total_items', 'N/A')}) ")
    lines.append("genera el 80% de las ventas.\n")
    
    # Clasificación ABC
    abc_summary = pareto.groupby('clasificacion').agg({
        'producto_id': 'count',
        'pct_valor': 'sum'
    }).reset_index()
    abc_summary.columns = ['Clasificación', 'Productos', '% Ventas']
    lines.append("\n**Clasificación ABC:**\n")
    lines.append(df_to_markdown(abc_summary))
    
    # ========== OUTLIERS ==========
    lines.append("\n---\n## ⚠️ Detección de Anomalías\n")
    outliers, outlier_stats = identificar_outliers(df, 'total')
    
    lines.append(f"\n**Método:** {outlier_stats['metodo']}")
    lines.append(f"\n**Outliers detectados:** {outlier_stats['outliers_count']} ({outlier_stats['outliers_pct']}%)")
    lines.append(f"\n**Límites:** [{outlier_stats.get('limite_inferior', 'N/A')}, {outlier_stats.get('limite_superior', 'N/A')}]")
    
    if len(outliers) > 0:
        lines.append("\n\n**Muestra de outliers:**\n")
        lines.append(df_to_markdown(outliers.head(5)))
    
    # ========== CONCLUSIONES ==========
    lines.append("\n---\n## 💡 Conclusiones\n")
    
    # Generar conclusiones automáticas basadas en datos
    mejor_tienda = tiendas.iloc[0]['tienda'] if len(tiendas) > 0 else 'N/A'
    mejor_dia = dias.iloc[dias['venta_total'].idxmax()]['dia_semana'] if len(dias) > 0 else 'N/A'
    
    lines.append(f"1. **Mejor tienda:** {mejor_tienda} con mayor volumen de ventas")
    lines.append(f"2. **Mejor día:** {mejor_dia} es el día con más ventas")
    lines.append(f"3. **Concentración:** Un pequeño grupo de productos genera la mayoría de ingresos (Pareto)")
    
    # Escribir archivo
    report_content = "\n".join(lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return str(output_file)
