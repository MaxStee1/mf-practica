"""
Clase base para repositorios
"""

from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass
from supabase import Client

from src.db.connection import get_supabase_client

@dataclass
class QueryResults:
    """Resultado estandar de una consulta"""
    succes: bool
    data: Any = None
    error: str | None = None
    count: int = 0

class BaseRepository(ABC):
    """ Clase base abstracta para repositorios."""
    
    def __init__(self):
        self._client: Client = get_supabase_client()
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Nombre de la tabla en Supabase"""
        pass
    
    def _handle_response(self, response) -> QueryResults:
        """Procesa la respuesta del cliente Supabase."""
        if response.data is not None:
            return QueryResults(
                succes=True,
                data=response.data,
                count=len(response.data) if isinstance(response.data, list) else 1
            )
        
        return QueryResults(
            succes=False,
            error="No se devolvieron datos de Supabase"
        )
    
    def get_all(self, limit: int = 100) -> QueryResults:
        """Obtiene todos los registros de la tabla"""
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*")
                .limit(limit)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
    
    def get_by_id(self, id:int) -> QueryResults:
        """Obtiene un registro por ID"""
        try:
            response = (
                self._client
                .table(self.table_name)
                .select("*")
                .eq("id", id)
                .single()
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
    
    def create(self, data: dict) -> QueryResults:
        """Crea un nuevo registro"""
        try:
            response=(
                self._client
                .table(self.table_name)
                .insert(data)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
        
    def update(self, id: int, data: dict):
        try:
            response=(
                self._client
                .table(self.table_name)
                .update(data)
                .eq("id", id)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))
        
    def delete(self, id: int) -> QueryResults:
        """Elimina un registro (hard delete)"""
        try:
            response=(
                self._client
                .table(self.table_name)
                .delete()
                .eq("id", id)
                .execute()
            )
            return self._handle_response(response)
        except Exception as e:
            return QueryResults(succes=False, error=str(e))