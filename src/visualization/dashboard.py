"""
Generación de dashboard multi-gráfico.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime

from src.visualization.config import (
    COLORS, PALETTE_MAIN, FIGURE_SIZES,
    setup_style, save_figure, format_currency
)


def generate_dashboard(
    df: pd.DataFrame,
    titulo: str = "Dashboard de Ventas",
    save_path: str = "dashboard_ventas.png"
) -> plt.Figure:
    """
    Genera un dashboard con múltiples visualizaciones.
    
    Args:
        df: DataFrame con datos de ventas
        titulo: Título del dashboard
        save_path: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    setup_style()
    
    # Preparar datos
    df = df.copy()
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Crear figura con grid personalizado
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Título principal
    fig.suptitle(
        titulo, 
        fontsize=20, 
        fontweight='bold',
        y=0.98
    )
    
    # Subtítulo con fecha
    fig.text(
        0.5, 0.94, 
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ha='center',
        fontsize=11,
        color=COLORS['neutral']
    )
    
    # ========== 1. KPIs en tarjetas (fila superior) ==========
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis('off')
    
    # Calcular KPIs
    venta_total = df['total'].sum()
    ticket_promedio = df['total'].mean()
    num_transacciones = len(df)
    unidades_totales = df['cantidad'].sum()
    
    kpis = [
        ('Venta Total', format_currency(venta_total), COLORS['primary']),
        ('Ticket Promedio', format_currency(ticket_promedio), COLORS['secondary']),
        ('Transacciones', f"{num_transacciones:,}", COLORS['success']),
        ('Unidades Vendidas', f"{unidades_totales:,}", COLORS['warning']),
    ]
    
    # Dibujar tarjetas de KPIs
    for i, (label, value, color) in enumerate(kpis):
        x_pos = 0.1 + i * 0.22
        
        # Rectángulo de fondo
        rect = plt.Rectangle(
            (x_pos, 0.1), 0.18, 0.8,
            transform=ax_kpi.transAxes,
            facecolor=color,
            alpha=0.1,
            edgecolor=color,
            linewidth=2
        )
        ax_kpi.add_patch(rect)
        
        # Valor
        ax_kpi.text(
            x_pos + 0.09, 0.55, value,
            transform=ax_kpi.transAxes,
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color=color
        )
        
        # Label
        ax_kpi.text(
            x_pos + 0.09, 0.3, label,
            transform=ax_kpi.transAxes,
            ha='center', va='center',
            fontsize=10,
            color=COLORS['text']
        )
    
    # ========== 2. Evolución temporal (izquierda media) ==========
    ax_temporal = fig.add_subplot(gs[1, :2])
    
    ventas_dia = df.groupby('fecha')['total'].sum()
    ax_temporal.fill_between(ventas_dia.index, ventas_dia.values, alpha=0.3, color=COLORS['primary'])
    ax_temporal.plot(ventas_dia.index, ventas_dia.values, color=COLORS['primary'], linewidth=2)
    ax_temporal.set_title('Evolución de Ventas Diarias', fontweight='bold')
    ax_temporal.set_xlabel('')
    ax_temporal.set_ylabel('Ventas ($)')
    ax_temporal.tick_params(axis='x', rotation=45)
    
    # ========== 3. Pie de tiendas (derecha media) ==========
    ax_pie = fig.add_subplot(gs[1, 2])
    
    ventas_tienda = df.groupby('tienda')['total'].sum()
    colors_pie = sns.color_palette(PALETTE_MAIN, len(ventas_tienda))
    
    wedges, texts, autotexts = ax_pie.pie(
        ventas_tienda.values,
        labels=ventas_tienda.index,
        colors=colors_pie,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.75
    )
    
    # Donut
    centre = plt.Circle((0, 0), 0.50, fc='white')
    ax_pie.add_patch(centre)
    ax_pie.set_title('Distribución por Tienda', fontweight='bold')
    
    # ========== 4. Top productos (izquierda inferior) ==========
    ax_productos = fig.add_subplot(gs[2, 0])
    
    if 'producto' in df.columns:
        top_productos = df.groupby('producto')['total'].sum().nlargest(5)
    else:
        top_productos = df.groupby('producto_id')['total'].sum().nlargest(5)
    
    colors_bar = sns.color_palette(PALETTE_MAIN, len(top_productos))
    ax_productos.barh(range(len(top_productos)), top_productos.values, color=colors_bar)
    ax_productos.set_yticks(range(len(top_productos)))
    ax_productos.set_yticklabels(top_productos.index)
    ax_productos.set_title('Top 5 Productos', fontweight='bold')
    ax_productos.set_xlabel('Ventas ($)')
    ax_productos.invert_yaxis()
    
    # ========== 5. Ventas por día de semana (centro inferior) ==========
    ax_diasemana = fig.add_subplot(gs[2, 1])
    
    df['dia_semana'] = df['fecha'].dt.day_name()
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ventas_dia_semana = df.groupby('dia_semana')['total'].sum().reindex(dias_orden)
    
    colors_dias = [COLORS['primary'] if v == ventas_dia_semana.max() else COLORS['neutral'] 
                   for v in ventas_dia_semana.values]
    
    ax_diasemana.bar(range(len(ventas_dia_semana)), ventas_dia_semana.values, color=colors_dias)
    ax_diasemana.set_xticks(range(len(ventas_dia_semana)))
    ax_diasemana.set_xticklabels(['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'])
    ax_diasemana.set_title('Ventas por Día de Semana', fontweight='bold')
    ax_diasemana.set_ylabel('Ventas ($)')
    
    # ========== 6. Distribución de tickets (derecha inferior) ==========
    ax_hist = fig.add_subplot(gs[2, 2])
    
    sns.histplot(
        data=df, 
        x='total', 
        bins=20, 
        kde=True,
        color=COLORS['primary'],
        alpha=0.7,
        ax=ax_hist
    )
    ax_hist.axvline(
        df['total'].mean(), 
        color=COLORS['danger'], 
        linestyle='--', 
        label=f"Media: {format_currency(df['total'].mean())}"
    )
    ax_hist.set_title('Distribución de Tickets', fontweight='bold')
    ax_hist.set_xlabel('Valor ($)')
    ax_hist.legend(fontsize=8)
    
    # Guardar
    if save_path:
        save_figure(fig, save_path, dpi=150)
    
    return fig
