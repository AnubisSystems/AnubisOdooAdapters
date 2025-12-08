import requests
import random

from anubis_core.features.product.models import CoreCategory
from anubis_core.features.product.ports import ICategoryAdapter
from anubis_odoo_adapters.tools.connection import call_odoo

class OdooCategotiesAdapter(ICategoryAdapter):
    def __init__(self, url_odoo: str, db_odoo: str, user_odoo: str, password_odoo: str):
        self.url_odoo = url_odoo
        self.db_odoo = db_odoo
        self.user_odoo = user_odoo
        self.password_odoo = password_odoo
        self.endpoint = f"{url_odoo}/jsonrpc"

        print ("pas")

        # Autenticación
        self.uid = call_odoo(self.endpoint, "common", "login", db_odoo, user_odoo, password_odoo)
        if not self.uid:
            print("Error de autenticación")
            exit()

    
    def get_category(self, id_category=None, depth=0) -> CoreCategory:
        pass

    def create_category(self, category: CoreCategory) -> CoreCategory:
        category_id = call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.public.category', 'create', [{
                'name': category.nombre,
                'parent_id': category.padre,
                'website_id' : category.sitio_web_id ,
                # 'website_published': category.activo
            }]
        )
        category.id = category_id
        return category

    def send_category(self, category: CoreCategory) -> CoreCategory:
        pass

    def disable_category(self, category: CoreCategory) -> bool:
        pass

    def disable_category(self, id) -> bool:
        pass    