from backend.services.api.user_service import UserService 
from backend.models import model 

class UserGoogleService(UserService):

    async def add_new_user(self, email: str): 
        user = model.User(email=email,
                        auth_provider=model.AuthProvider.Google,
                        hashed_password="")
        
        return await self.save_entity(user)
 


