""" Adaptador de productos para odoo ecommerce.


"""
import requests
import random

from anubis_product_core.models import CoreProduct
from anubis_product_core.interfaces import IProductAdapter

class OdooProductAdapter(IProductAdapter):
    def __init__(self, url_odoo: str, db_odoo: str, user_odoo: str, password_odoo: str):
        self.url_odoo = url_odoo
        self.db_odoo = db_odoo
        self.user_odoo = user_odoo
        self.password_odoo = password_odoo
        self.endpoint = f"{url_odoo}/jsonrpc"

        # Autenticación
        self.uid = self._call("common", "login", db_odoo, user_odoo, password_odoo)
        if not self.uid:
            print("Error de autenticación")
            exit()

    def _call(self, service, method, *args):
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args
            },
            "id": random.randint(0, 1000000000)
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.endpoint, json=payload, headers=headers)
        result = response.json()
        if "error" in result:
            raise Exception(result["error"])
        return result["result"]

    def get_product(self, id_product: int) -> CoreProduct:
        productos_odoo = self._call("object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.template', 'search_read',
            [[['id', '=', id_product]]],
            {'fields': ['id', 'name', 'list_price', 'image_1024']}
        )
        if not productos_odoo:
            print(f"No se encontró un producto con ID {id_product}")
            return None

        producto_odoo = productos_odoo[0]
        product = CoreProduct(
            id=producto_odoo["id"],
            name=producto_odoo["name"],
            price=producto_odoo["list_price"],
            images_base64=[producto_odoo["image_1024"]]
        )
        print("Producto encontrado:", producto_odoo)
        print("Producto 2 encontrado:", product)
        return product

    def create_product(self, product: CoreProduct):
        tags_id = [self.get_or_create_tag_id(tag) for tag in product.tags]

        product_id = self._call("object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.template', 'create', [{
                'name': product.name,
                'type': 'consu',
                'list_price': product.price,
                'standard_price': product.price_cost,
                'default_code': product.default_code,
                'categ_id': 1,
                'public_categ_ids': product.categories,
                'sale_ok': True,
                'website_published': True,
                'description': product.ia_descripcion,
                'description_sale': product.store_description,
                'description_ecommerce': product.ecommerce_description,
                'image_1920': product.images_base64[0],
                'product_tag_ids': tags_id
            }]
        )
        product.id = product_id
        return product

    def send_product(self, product: CoreProduct) -> CoreProduct:
        pass

    def get_or_create_tag_id(self, tag_name):
        tags = self._call("object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.tag', 'search_read',
            [[['name', '=', tag_name]]],
            {'fields': ['id', 'name']}
        )
        if tags:
            return tags[0]['id']
        tag_id = self._call("object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.tag', 'create',
            [{'name': tag_name}]
        )
        return tag_id

    def search_id(self, page, rows, *args, **kwargs) -> list[str]:
        offset = (page - 1) * rows
        ids = self._call("object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'product.template', 'search_read',
            [],
            {'offset': offset, 'limit': rows, 'fields': ['id']}
        )
        return [str(i["id"]) for i in ids]