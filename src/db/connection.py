"""
Módulo de conexión a Supabase.
"""
from supabase import create_client, Client
from src.config.settings import SUPABASE_URL, SUPABASE_KEY

# Cliente singleton
_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Obtiene el cliente de Supabase (singleton).

    Returns:
        Cliente de Supabase inicializado

    Raises:
        ConnectionError: Si no se puede conectar
    """
    global _client

    if _client is None:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            raise ConnectionError(f"Error conectando a Supabase: {e}")

    return _client


def test_connection() -> bool:
    """
    Prueba la conexión a Supabase.
    """
    try:
        client = get_supabase_client()
        client.table("categorias").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False
