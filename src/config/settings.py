"""
Carga variables de entorno de forma segura
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener la ruta a la raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

# Cargar variables de entorno desde .env
load_dotenv(dotenv_path=ENV_PATH)

def get_env_variable(var_name: str, required: bool = True) -> str | None:
    value = os.getenv(var_name)
    if required and not value:
        raise ValueError(
            f"Variable de entorno '{var_name}' no encontrada. "
            f"Asegurate de que esxiste en {ENV_PATH}"
        )
    return value

# Variables de Supabase
SUPABASE_URL = get_env_variable("SUPABASE_URL")
SUPABASE_KEY = get_env_variable("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = get_env_variable("SUPABASE_SERVICE_KEY", required=False)

"""
Calcula la ruta absoluta del .env desde cualquier archivo que lo importe.
Usa python-dotenv para cargar las variables de entorno.
Función get_env_variable:
    Lanza error si la variable es requerida y no existe.
    Permite variables opcionales.
Expones las variables como constantes (SUPABASE_URL, SUPABASE_KEY, etc.)
Esto evita tener credenciales hardcodeadas en tu código.
"""