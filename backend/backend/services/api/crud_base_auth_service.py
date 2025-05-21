from typing import Generic
from .crud_base_service import CrudBaseService, T
from abc import ABC, abstractmethod
from fastapi import HTTPException, status

class CrudBaseAuthService(CrudBaseService, ABC, Generic[T]):
    
    def _raise(self, detail: str = "Not authorized for this action.", status=status.HTTP_403_FORBIDDEN):

        raise HTTPException(
                status_code=status,
                detail=detail
            )
    
    async def delete(self, entity: T):

        if not await self.can_delete(entity):
            self._raise()
        
        return await super().delete(entity)

    async def get_by_id(self, id, mask_class = None):

        entity = await super().get_by_id(id, mask_class)
        
        if not entity:
            self._raise(f"{id=} not found", status.HTTP_404_NOT_FOUND)
        
        if not await self.can_view(entity):
            self._raise()
        
        return entity
    
    async def update(self, update_model, /, id = None, entity = None, patch = True):
        
        entity = await self._entity(entity, id)

        if not await self.can_update(entity):
            self._raise()

        result = await super().update(update_model, entity=entity, patch=patch)
        return result

    @abstractmethod
    async def can_delete(self, entity: T) -> bool:
        ...

    @abstractmethod
    async def can_view(self, entity: T) -> bool:
        ...

    @abstractmethod
    async def can_update(self, entity: T) -> bool:
        ...