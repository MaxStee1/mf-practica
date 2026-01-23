"""
Funciones para crear gráficos individuales.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Tuple, Optional

from src.visualization.config import (
    COLORS, PALETTE_MAIN, FIGURE_SIZES, 
    setup_style, save_figure, format_currency
)


def plot_ventas_temporales(
    df: pd.DataFrame,
    fecha_col: str = 'fecha',
    valor_col: str = 'total',
    periodo: str = 'D',
    titulo: str = 'Evolución de Ventas',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Gráfico de línea temporal de ventas.
    
    Args:
        df: DataFrame con datos
        fecha_col: Columna de fecha
        valor_col: Columna de valor
        periodo: 'D'=día, 'W'=semana, 'M'=mes
        titulo: Título del gráfico
        save_path: Ruta para guardar (opcional)
    
    Returns:
        Figura de matplotlib
    """
    setup_style()
    
    # Preparar datos
    df = df.copy()
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    
    datos = df.groupby(pd.Grouper(key=fecha_col, freq=periodo))[valor_col].sum()
    datos = datos.reset_index()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['wide'])
    
    # Línea principal
    ax.plot(
        datos[fecha_col], 
        datos[valor_col],
        color=COLORS['primary'],
        linewidth=2,
        marker='o',
        markersize=5
    )
    
    # Área bajo la curva
    ax.fill_between(
        datos[fecha_col], 
        datos[valor_col],
        alpha=0.2,
        color=COLORS['primary']
    )
    
    # Formateo
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Ventas ($)')
    
    # Formato de fechas en eje X
    if periodo == 'D':
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    elif periodo == 'M':
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    plt.xticks(rotation=45)
    
    # Formato de moneda en eje Y
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: format_currency(x))
    )
    
    # Agregar línea de promedio
    promedio = datos[valor_col].mean()
    ax.axhline(
        y=promedio, 
        color=COLORS['danger'], 
        linestyle='--', 
        linewidth=1,
        label=f'Promedio: {format_currency(promedio)}'
    )
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig


def plot_barras_categoria(
    df: pd.DataFrame,
    categoria_col: str = 'categoria',
    valor_col: str = 'total',
    titulo: str = 'Ventas por Categoría',
    horizontal: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Gráfico de barras por categoría.
    """
    setup_style()
    
    # Agregar datos
    datos = df.groupby(categoria_col)[valor_col].sum().sort_values(ascending=True)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['medium'])
    
    # Colores degradados
    colors = sns.color_palette(PALETTE_MAIN, len(datos))
    
    if horizontal:
        bars = ax.barh(datos.index, datos.values, color=colors)
        ax.set_xlabel('Ventas ($)')
        ax.set_ylabel('')
        
        # Agregar valores en las barras
        for bar, value in zip(bars, datos.values):
            ax.text(
                value + datos.max() * 0.01, 
                bar.get_y() + bar.get_height()/2,
                format_currency(value),
                va='center',
                fontsize=10
            )
    else:
        bars = ax.bar(datos.index, datos.values, color=colors)
        ax.set_ylabel('Ventas ($)')
        plt.xticks(rotation=45, ha='right')
        
        for bar, value in zip(bars, datos.values):
            ax.text(
                bar.get_x() + bar.get_width()/2, 
                value + datos.max() * 0.01,
                format_currency(value),
                ha='center',
                fontsize=9
            )
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig


def plot_distribucion_pie(
    df: pd.DataFrame,
    categoria_col: str = 'tienda',
    valor_col: str = 'total',
    titulo: str = 'Distribución de Ventas',
    donut: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Gráfico circular (pie/donut).
    """
    setup_style()
    
    # Agregar datos
    datos = df.groupby(categoria_col)[valor_col].sum()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['square'])
    
    # Colores
    colors = sns.color_palette(PALETTE_MAIN, len(datos))
    
    # Crear pie
    wedges, texts, autotexts = ax.pie(
        datos.values,
        labels=datos.index,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.75 if donut else 0.6,
        explode=[0.02] * len(datos)
    )
    
    # Estilo de texto
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Convertir a donut
    if donut:
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        ax.add_patch(centre_circle)
        
        # Total en el centro
        total = datos.sum()
        ax.text(
            0, 0, 
            f'Total\n{format_currency(total)}',
            ha='center', va='center',
            fontsize=14, fontweight='bold'
        )
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig

# Continuación de charts.py

def plot_histograma_tickets(
    df: pd.DataFrame,
    valor_col: str = 'total',
    bins: int = 30,
    titulo: str = 'Distribución de Tickets',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Histograma de distribución de tickets.
    """
    setup_style()
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['medium'])
    
    # Histograma con KDE
    sns.histplot(
        data=df, 
        x=valor_col, 
        bins=bins,
        kde=True,
        color=COLORS['primary'],
        alpha=0.7,
        ax=ax
    )
    
    # Líneas de estadísticas
    media = df[valor_col].mean()
    mediana = df[valor_col].median()
    
    ax.axvline(media, color=COLORS['danger'], linestyle='--', linewidth=2, label=f'Media: {format_currency(media)}')
    ax.axvline(mediana, color=COLORS['success'], linestyle='-.', linewidth=2, label=f'Mediana: {format_currency(mediana)}')
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Valor del Ticket ($)')
    ax.set_ylabel('Frecuencia')
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig


def plot_boxplot_categorias(
    df: pd.DataFrame,
    categoria_col: str = 'categoria',
    valor_col: str = 'total',
    titulo: str = 'Distribución por Categoría',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Box plot comparativo por categoría.
    """
    setup_style()
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['medium'])
    
    # Box plot con seaborn
    sns.boxplot(
        data=df,
        x=categoria_col,
        y=valor_col,
        palette=PALETTE_MAIN,
        ax=ax
    )
    
    # Agregar puntos (strip plot)
    sns.stripplot(
        data=df,
        x=categoria_col,
        y=valor_col,
        color=COLORS['text'],
        alpha=0.3,
        size=4,
        ax=ax
    )
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('')
    ax.set_ylabel('Valor ($)')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig


def plot_heatmap_ventas(
    df: pd.DataFrame,
    fecha_col: str = 'fecha',
    valor_col: str = 'total',
    titulo: str = 'Mapa de Calor - Ventas por Día',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Heatmap de ventas por día de semana y semana del mes.
    """
    setup_style()
    
    df = df.copy()
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    
    # Crear columnas de día y semana
    df['dia_semana'] = df[fecha_col].dt.day_name()
    df['semana'] = df[fecha_col].dt.isocalendar().week
    
    # Pivot table
    pivot = df.pivot_table(
        values=valor_col,
        index='dia_semana',
        columns='semana',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reordenar días
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_presentes = [d for d in dias_orden if d in pivot.index]
    pivot = pivot.reindex(dias_presentes)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['wide'])
    
    # Heatmap
    sns.heatmap(
        pivot,
        annot=True,
        fmt=',.0f',
        cmap='YlOrRd',
        linewidths=0.5,
        ax=ax,
        cbar_kws={'label': 'Ventas ($)'}
    )
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Semana del Año')
    ax.set_ylabel('')
    
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig


def plot_tendencia_con_prediccion(
    df: pd.DataFrame,
    fecha_col: str = 'fecha',
    valor_col: str = 'total',
    titulo: str = 'Tendencia de Ventas',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Gráfico de tendencia con línea de regresión.
    """
    setup_style()
    
    df = df.copy()
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    
    # Agregar por día
    datos = df.groupby(fecha_col)[valor_col].sum().reset_index()
    datos['dia_num'] = range(len(datos))
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZES['wide'])
    
    # Puntos de datos
    ax.scatter(
        datos[fecha_col], 
        datos[valor_col],
        color=COLORS['primary'],
        alpha=0.6,
        s=50,
        label='Ventas diarias'
    )
    
    # Línea de tendencia (regresión lineal)
    z = np.polyfit(datos['dia_num'], datos[valor_col], 1)
    p = np.poly1d(z)
    
    ax.plot(
        datos[fecha_col], 
        p(datos['dia_num']),
        color=COLORS['danger'],
        linewidth=2,
        linestyle='--',
        label=f'Tendencia (pendiente: {z[0]:,.0f}/día)'
    )
    
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Ventas ($)')
    ax.legend()
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        save_figure(fig, save_path)
    
    return fig
