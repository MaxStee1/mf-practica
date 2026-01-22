import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class DataFrameInfo:
    """Información general de un DataFrame."""
    rows: int
    columns: int
    memory_mb: float
    dtypes: dict
    column_names: list
    
def describe_dataframe(df: pd.DataFrame) -> DataFrameInfo:
    """Obtiene información general del DataFrame."""
    return DataFrameInfo(
        rows=len(df),
        columns=len(df.columns),
        memory_mb=df.memory_usage(deep=True).sum() / 1024 / 1024,
        dtypes=df.dtypes.astype(str).to_dict(),
        column_names=df.columns.tolist()
    )
    
def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Analiza valores faltantes en el DataFrame."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    result = pd.DataFrame({
        'columna': df.columns,
        'nulos': missing.values,
        'porcentaje': missing_pct.values
    })

    return result[result['nulos'] > 0].sort_values('nulos', ascending=False)

def check_duplicates(df: pd.DataFrame, subset: list = None) -> dict:
    """Detecta filas duplicadas."""
    if subset:
        duplicados = df.duplicated(subset=subset, keep=False)
    else:
        duplicados = df.duplicated(keep=False)

    return {
        'total_filas': len(df),
        'filas_duplicadas': duplicados.sum(),
        'filas_unicas': (~duplicados).sum(),
        'porcentaje_duplicados': round(duplicados.sum() / len(df) * 100, 2)
    }
    
def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Estadísticas descriptivas de columnas numéricas."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) == 0:
        return pd.DataFrame()

    summary = df[numeric_cols].describe().T
    summary['missing'] = df[numeric_cols].isnull().sum()
    summary['zeros'] = (df[numeric_cols] == 0).sum()

    return summary.round(2)

def get_categorical_summary(df: pd.DataFrame, max_categories: int = 10) -> dict:
    """Resumen de columnas categóricas."""
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    result = {}
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        result[col] = {
            'unique_values': df[col].nunique(),
            'top_values': value_counts.head(max_categories).to_dict(),
            'null_count': df[col].isnull().sum()
        }

    return result

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula matriz de correlación para columnas numéricas."""
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr().round(3)