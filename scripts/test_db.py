from src.db.connection import test_connection
from src.db.repositories.categoria import CategoriaRepository
from src.db.repositories.producto import ProductoRepository

def print_section(tittle: str):
    print(f"\n{'=' * 60}")
    print(f" {tittle} ")
    print('=' * 60)

def main():
    # 1. Test de conexion
    print_section("TEST DE CONEXION")
    if not test_connection():
        print("Error de conexion. Revisa tu configuracion.")
        return
    print("Conexion exitosa")
    
    cat_repo = CategoriaRepository()
    prod_repo = ProductoRepository()
    
    # 2. Listar categorias
    print_section("Listar Categorias")
    result = cat_repo.get_all()
    if not result.succes:
        print(f"Error: {result.error}")
        return
    
    for cat in result.data:
        print(f" - {cat['id']}: {cat['nombre']}")
    print(f"Total: {result.count}")
    
    # Usar la primera categoria
    categoria_id = result.data[0]["id"]
    
    # 3. Crear producto de prueba
    print_section("CREAR PRODUCTO DE PRUEBA")
    nuevo_producto = {
        "nombre": "Producto Test Python",
        "descripcion": "Producto creado desde test_db.py",
        "precio": 4.99,
        "stock": 10,
        "categoria_id": categoria_id,
        "activo": True
    }
    
    result = prod_repo.create(nuevo_producto)
    if not result.succes:
        print(f"Error creando producto: {result.error}")
        return
    
    producto = result.data[0]
    producto_id = producto["id"]
    
    print(f"Producto creado con ID {producto_id}")
    
    
    # 4. Actualizar stock
    print_section("ACTUALIZAR STOCK")
    result = prod_repo.update_stock(producto_id, 25)
    if result.succes:
        print("Stock actualizado a 25")
    else:
        print(f"Error: {result.error}")
        
    
    # 5. Buscar productos por categoría
    print_section("PRODUCTOS POR CATEGORÍA")
    result = prod_repo.get_by_categoria(categoria_id)
    if result.succes:
        for p in result.data:
            cat_nombre = p.get("categorias", {}).get("nombre", "N/A")
            print(f" - {p['nombre']} (${p['precio']}) [{cat_nombre}]")
        print(f"Total: {result.count}")
    else:
        print(f"Error: {result.error}")
        
     # 6. Soft delete
    print_section("SOFT DELETE")
    result = prod_repo.soft_delete(producto_id)
    if result.succes:
        print(f"Producto {producto_id} desactivado")
    else:
        print(f"Error: {result.error}")
        
    # 7. Verificar que no aparece en activos
    print_section("VERIFICAR ACTIVOS")
    result = prod_repo.get_activos()
    if result.succes:
        ids = [p["id"] for p in result.data]
        if producto_id not in ids:
            print("Producto no aparece en activos")
        else:
            print("Producto aún aparece como activo")
            
    # 8. Limpieza final (hard delete)
    print_section("LIMPIEZA")
    result = prod_repo.delete(producto_id)
    if result.succes:
        print(f"Producto {producto_id} eliminado definitivamente")
    else:
        print(f"Error al eliminar: {result.error}")

    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS CORRECTAMENTE")
    print("=" * 60)

if __name__ == "__main__":
    main()