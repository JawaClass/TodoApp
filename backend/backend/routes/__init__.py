from . import auth_route, signup_route, todo_item, user_route


routers = [
    auth_route.router,
    signup_route.router,
    todo_item.router,
    user_route.router
]