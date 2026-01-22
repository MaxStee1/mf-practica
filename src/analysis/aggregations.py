"""
Módulo de agregaciones y agrupaciones.
"""
import pandas as pd
import numpy as np


def ventas_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa ventas por categoría de producto."""
    agg = df.groupby('categoria').agg({
        'total': ['sum', 'mean', 'count'],
        'cantidad': ['sum', 'mean']
    }).round(2)

    agg.columns = ['_'.join(col) for col in agg.columns]
    agg = agg.reset_index()

    agg.columns = [
        'categoria',
        'venta_total',
        'venta_promedio',
        'num_transacciones',
        'unidades_totales',
        'unidades_promedio'
    ]

    return agg.sort_values('venta_total', ascending=False)


def ventas_por_periodo(
    df: pd.DataFrame,
    periodo: str = 'D',
    fecha_col: str = 'fecha'
) -> pd.DataFrame:
    """
    Agrupa ventas por periodo temporal.
    """
    df = df.copy()
    df[fecha_col] = pd.to_datetime(df[fecha_col])

    agg = (
    df.groupby(pd.Grouper(key=fecha_col, freq=periodo))
        .agg(
            venta_total=('total', 'sum'),
            unidades=('cantidad', 'sum'),
            transacciones=('total', 'count')
        )
        .reset_index()
    )

    agg.columns = ['periodo', 'venta_total', 'unidades', 'transacciones']
    agg['ticket_promedio'] = (agg['venta_total'] / agg['transacciones']).round(2)

    return agg


def ranking_productos(
    df: pd.DataFrame,
    top_n: int = 10,
    metric: str = 'total'
) -> pd.DataFrame:
    """
    Ranking de productos.
    """
    if metric == 'count':
        ranking = df.groupby('producto_id').size().reset_index(name='frecuencia')
        ranking = ranking.sort_values('frecuencia', ascending=False)
    else:
        ranking = df.groupby('producto_id').agg({
            'total': 'sum',
            'cantidad': 'sum'
        }).reset_index()
        ranking = ranking.sort_values(metric, ascending=False)

    ranking['rank'] = range(1, len(ranking) + 1)
    return ranking.head(top_n)


def ranking_vendedores(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Ranking de vendedores."""
    ranking = df.groupby('vendedor').agg(
        total=('total', 'sum'),
        cantidad=('cantidad', 'sum'),
        transacciones=('producto_id', 'count')  # ✅ reemplaza 'id'
    ).reset_index()


    ranking.columns = ['vendedor', 'venta_total', 'unidades', 'transacciones']
    ranking['ticket_promedio'] = (ranking['venta_total'] / ranking['transacciones']).round(2)
    ranking = ranking.sort_values('venta_total', ascending=False)
    ranking['rank'] = range(1, len(ranking) + 1)

    return ranking.head(top_n)


def ventas_por_tienda(df: pd.DataFrame) -> pd.DataFrame:
    """Comparativa de ventas entre tiendas."""
    tiendas = df.groupby('tienda').agg({
        'total': ['sum', 'mean', 'count'],
        'cantidad': 'sum'
    }).round(2)

    tiendas.columns = ['venta_total', 'ticket_promedio', 'transacciones', 'unidades']
    tiendas = tiendas.reset_index()
    tiendas['participacion_pct'] = (
        tiendas['venta_total'] / tiendas['venta_total'].sum() * 100
    ).round(2)

    return tiendas.sort_values('venta_total', ascending=False)


def analisis_dia_semana(df: pd.DataFrame, fecha_col: str = 'fecha') -> pd.DataFrame:
    """Análisis de ventas por día de la semana."""
    df = df.copy()
    df = df.copy()

    df['fecha'] = pd.to_datetime(df['fecha'])
    df['dia_semana'] = df['fecha'].dt.day_name()
    df['dia_num'] = df['fecha'].dt.weekday  # lunes=0, domingo=6

    dias = df.groupby(['dia_semana', 'dia_num']).agg(
        venta_total=('total', 'sum'),
        venta_promedio=('total', 'mean'),
        transacciones=('total', 'count')
    ).reset_index()

    dias = dias.sort_values('dia_num')


    return dias[['dia_semana', 'venta_total', 'venta_promedio', 'transacciones']]
