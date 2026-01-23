"""
Configuración de estilos para visualizaciones.
"""
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Crear directorio de outputs si no existe
CHARTS_DIR = Path("outputs/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Paleta de colores corporativa
COLORS = {
    'primary': '#2E86AB',      # Azul principal
    'secondary': '#A23B72',    # Magenta
    'success': '#38B000',      # Verde
    'warning': '#F77F00',      # Naranja
    'danger': '#D62828',       # Rojo
    'neutral': '#6C757D',      # Gris
    'background': '#F8F9FA',   # Fondo claro
    'text': '#212529',         # Texto oscuro
}

# Paleta secuencial para múltiples categorías
PALETTE_MAIN = [
    '#2E86AB', '#A23B72', '#38B000', '#F77F00', 
    '#D62828', '#6C757D', '#17A2B8', '#FFC107'
]

# Tamaños de figura estándar
FIGURE_SIZES = {
    'small': (8, 5),
    'medium': (10, 6),
    'large': (12, 8),
    'wide': (14, 6),
    'square': (8, 8),
    'dashboard': (16, 12),
}


def setup_style():
    """
    Configura el estilo global de matplotlib/seaborn.
    Llamar al inicio de cada script de visualización.
    """
    # Estilo de seaborn
    sns.set_theme(style="whitegrid", palette=PALETTE_MAIN)
    
    # Configuración de matplotlib
    plt.rcParams.update({
        # Fuentes
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica'],
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        
        # Colores
        'axes.facecolor': COLORS['background'],
        'figure.facecolor': 'white',
        'text.color': COLORS['text'],
        'axes.labelcolor': COLORS['text'],
        'xtick.color': COLORS['text'],
        'ytick.color': COLORS['text'],
        
        # Grid
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        
        # Otros
        'figure.dpi': 100,
        'savefig.dpi': 150,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.2,
    })


def save_figure(fig, filename: str, dpi: int = 150):
    """
    Guarda una figura en el directorio de charts.
    
    Args:
        fig: Figura de matplotlib
        filename: Nombre del archivo (con extensión)
        dpi: Resolución
    """
    filepath = CHARTS_DIR / filename
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"✅ Guardado: {filepath}")
    return filepath


def format_currency(value: float) -> str:
    """Formatea un valor como moneda."""
    return f"${value:,.0f}"


def format_percentage(value: float) -> str:
    """Formatea un valor como porcentaje."""
    return f"{value:.1f}%"
