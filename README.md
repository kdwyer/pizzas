# Pizza Shop

This is a toy pizza ordering website, for experimentation.

Don't use this to power your pizza enterprise :-)


## Database Migrations

`cd pizzas/order`

`PYTHONPATH=. alembic revision --autogenerate -m "Something descriptive"`

`PYTHONPATH=. alembic upgrade head`
