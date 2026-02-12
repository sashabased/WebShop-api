from fastapi import FastAPI
from routers import users, cart, items, order

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)
app.include_router(cart.router)
app.include_router(order.router)