"""
Repositorio para la tabla categorias.
"""
from src.db.repositories.base import BaseRepository, QueryResults

class CategoriaRepository(BaseRepository):
    """Repositorio para operaciones CRUD de categorías."""

    @property
    def table_name(self) -> str:
        return "categorias"

    def get_by_nombre(self, nombre: str) -> QueryResults:
        """
        Busca categorías cuyo nombre coincida parcialmente.
        """
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*")
                .ilike("nombre", f"%{nombre}%")
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))

    def get_with_product_count(self) -> QueryResults:
        """
        Obtiene categorías junto con el conteo de productos asociados.
        """
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*, productos(count)")
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
