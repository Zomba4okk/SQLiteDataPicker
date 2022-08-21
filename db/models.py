from sqlalchemy.ext.automap import automap_base

from db.meta import engine

__all__ = (
    "Customer",
    "Invoice",
)


base = automap_base()
base.prepare(autoload_with=engine)

Customer = base.classes.Customer
Invoice = base.classes.Invoice
