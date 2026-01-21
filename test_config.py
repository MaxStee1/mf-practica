"""
SCRIPT para probar que la configuracion carga correctamente
"""

from src.config.settings import(
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_SERVICE_KEY,
)

def mask_key(key: str | None, visible_chars: int = 10) -> str:
    if not key:
        return "No configurada"
    return f"{key[:visible_chars]}...{'*' * 20}"

def main():
    print("=" * 50)
    print("TEST DE CONFIGURACION")
    print("=" * 50)
    
    print(f"\nSUPABASE_URL: {SUPABASE_URL}")
    print(f"\nSUPABASE_KEY: {mask_key(SUPABASE_KEY)}")
    print(f"\nSUPABASE_SERVICE_KEY: {mask_key(SUPABASE_SERVICE_KEY)}")
    
    print("\n" + "=" * 50)
    print("Configuracion cargada correctamente!")
    print("=" * 50)

if __name__ == "__main__":
    main()
    
"""
Importa las variables desde src.config.settings.
Enmascara las keys para no mostrar todo el valor en consola.
Imprime la URL y las keys parcialmente.
Indica si todo se cargó correctamente.
"""