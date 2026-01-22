""" Repositorio para la tabla productos. """
from src.db.repositories.base import BaseRepository, QueryResults

class ProductoRepository(BaseRepository):
    """Repositorio para operaciones CRUD de productos."""

    @property
    def table_name(self) -> str:
        return "productos"

    def get_by_categoria(self, categoria_id: int) -> QueryResults:
        """Obtiene productos activos de una categoría específica."""
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*, categorias(nombre)")
                .eq("categoria_id", categoria_id)
                .eq("activo", True)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))

    def get_activos(self) -> QueryResults:
        """Obtiene todos los productos activos."""
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*, categorias(nombre)")
                .eq("activo", True)
                .order("nombre")
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))

    def update_stock(self, id: int, cantidad: int) -> QueryResults:
        """
        Establece el stock de un producto.

        Args:
            id: ID del producto
            cantidad: Cantidad absoluta de stock
        """
        if cantidad < 0:
            return QueryResults(
                succes=False,
                error="El stock no puede ser negativo"
            )

        return self.update(id, {"stock": cantidad})

    def ajustar_stock(self, id: int, ajuste: int) -> QueryResults:
        """
        Ajusta el stock sumando o restando una cantidad.
        """
        # Obtener stock actual
        result = self.get_by_id(id)
        if not result.succes:
            return result

        stock_actual = result.data.get("stock", 0)
        nuevo_stock = stock_actual + ajuste

        if nuevo_stock < 0:
            return QueryResults(
                succes=False,
                error=(
                    f"Stock insuficiente. "
                    f"Actual: {stock_actual}, Ajuste: {ajuste}"
                )
            )

        return self.update_stock(id, nuevo_stock)

    def soft_delete(self, id: int) -> QueryResults:
        """Desactiva un producto (soft delete)."""
        return self.update(id, {"activo": False})

    def restore(self, id: int) -> QueryResults:
        """Reactiva un producto desactivado."""
        return self.update(id, {"activo": True})

    def search(self, term: str) -> QueryResults:
        """Busca productos por nombre o descripción."""
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*, categorias(nombre)")
                .or_(f"nombre.ilike.%{term}%,descripcion.ilike.%{term}%")
                .eq("activo", True)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
