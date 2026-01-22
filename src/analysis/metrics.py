"""
Módulo de métricas de negocio.
"""
import pandas as pd
import numpy as np
from typing import Tuple


def calcular_ticket_promedio(df: pd.DataFrame) -> float:
    """
    Valor promedio por transacción.
    """
    return round(df['total'].mean(), 2)


def calcular_unidades_promedio(df: pd.DataFrame) -> float:
    """
    Unidades promedio por venta.
    """
    return round(df['cantidad'].mean(), 2)


def calcular_crecimiento(
    df: pd.DataFrame,
    periodo: str = 'M',
    fecha_col: str = 'fecha'
) -> pd.DataFrame:
    """
    Crecimiento periodo a periodo.
    """
    df = df.copy()
    df[fecha_col] = pd.to_datetime(df[fecha_col])

    ventas = df.groupby(pd.Grouper(key=fecha_col, freq=periodo))['total'].sum()
    ventas = ventas.reset_index()
    ventas.columns = ['periodo', 'venta']

    ventas['venta_anterior'] = ventas['venta'].shift(1)
    ventas['crecimiento_abs'] = ventas['venta'] - ventas['venta_anterior']
    ventas['crecimiento_pct'] = (
        (ventas['venta'] / ventas['venta_anterior'] - 1) * 100
    ).round(2)

    return ventas


def identificar_outliers(
    df: pd.DataFrame,
    columna: str,
    metodo: str = 'iqr'
) -> Tuple[pd.DataFrame, dict]:
    """
    Detecta valores atípicos con IQR o Z-score.
    """
    valores = df[columna].dropna()

    if metodo == 'iqr':
        Q1 = valores.quantile(0.25)
        Q3 = valores.quantile(0.75)
        IQR = Q3 - Q1

        lim_inf = Q1 - 1.5 * IQR
        lim_sup = Q3 + 1.5 * IQR

        mask = (df[columna] < lim_inf) | (df[columna] > lim_sup)

        stats = {
            'metodo': 'IQR',
            'Q1': round(Q1, 2),
            'Q3': round(Q3, 2),
            'IQR': round(IQR, 2),
            'limite_inferior': round(lim_inf, 2),
            'limite_superior': round(lim_sup, 2),
            'outliers_count': mask.sum(),
            'outliers_pct': round(mask.sum() / len(df) * 100, 2)
        }

    else:
        mean = valores.mean()
        std = valores.std()

        z = np.abs((df[columna] - mean) / std)
        mask = z > 3

        stats = {
            'metodo': 'Z-Score',
            'mean': round(mean, 2),
            'std': round(std, 2),
            'threshold': 3,
            'outliers_count': mask.sum(),
            'outliers_pct': round(mask.sum() / len(df) * 100, 2)
        }

    return df[mask].copy(), stats


def calcular_pareto(
    df: pd.DataFrame,
    grupo_col: str = 'producto_id',
    valor_col: str = 'total'
) -> pd.DataFrame:
    """
    Análisis Pareto 80/20.
    """
    pareto = df.groupby(grupo_col)[valor_col].sum().reset_index()
    pareto = pareto.sort_values(valor_col, ascending=False)

    total = pareto[valor_col].sum()
    pareto['pct_valor'] = (pareto[valor_col] / total * 100).round(2)
    pareto['pct_acumulado'] = pareto['pct_valor'].cumsum().round(2)

    def clasificar(pct):
        if pct <= 80:
            return 'A'
        elif pct <= 95:
            return 'B'
        return 'C'

    pareto['clasificacion'] = pareto['pct_acumulado'].apply(clasificar)

    items_80 = len(pareto[pareto['pct_acumulado'] <= 80])

    pareto.attrs['pareto_stats'] = {
        'items_80_pct_valor': items_80,
        'total_items': len(pareto),
        'pct_items_80_valor': round(items_80 / len(pareto) * 100, 2)
    }

    return pareto
