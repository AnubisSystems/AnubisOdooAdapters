import requests
import random

from anubis_core.features.customers.models import CoreCustomer, CoreCustomerAddress, CoreCustomerHistoryInvoice, CoreCustomerInvoice, CoreCustomersLoyalty, CustomerAdressTypes
from anubis_core.features.customers.ports import ICustomerAdapter
from anubis_odoo_adapters.tools.connection import call_odoo

class OdooCustomersAdapter(ICustomerAdapter):
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

    
    def get_customer_id(self, id_customer:int)-> CoreCustomer:        
        pass
    
    def get_customer_email(self, email:str)-> CoreCustomer:        
        pass
    
    def create_customer(self, customer: CoreCustomer)-> CoreCustomer:        
        return self.send_customer(customer)

    def send_customer(self, customer: CoreCustomer)-> CoreCustomer:        
        
        created_customer = self._send_customer(customer)
        customer.id = created_customer.id

        for direccion in customer.direcciones:
            created_address = self._send_address(customer.id,direccion)
            direccion.id = created_address.id

        for fidelidad in customer.puntos_fidelidad:
            created_loyalty = self._send_loyalty(customer.id, fidelidad)
            fidelidad = created_loyalty.id

        for factura in customer.facturas:
            created_factura = self._send_invoice(customer.id, factura)
            factura.id = created_factura.id

        return customer        

    def _send_customer(self, customer: CoreCustomer)-> CoreCustomer:        
        payload = {
            "name": f"{customer.nombre} {customer.apellido_1 or ''} {customer.apellido_2 or ''}".strip(),
            "email": customer.email,
            "vat": customer.nif,
            #"birthdate_date": customer.fecha_nacimiento.strftime("%Y-%m-%d") if customer.fecha_nacimiento else None,
            "customer_rank": 1,
            "website_id": customer.sitio_web_id,
            #"newsletter_optin": customer.boletin,
        }
        
        return_id = call_odoo(self.endpoint, "object", "execute_kw",
                self.db_odoo, self.uid, self.password_odoo,
                'res.partner', 'create', [payload]
            )
        
        customer.id = return_id



        return customer
    
    def _send_user(self, customer: CoreCustomer):
        payload = {
            "name": f"{customer.nombre} {customer.apellido_1 or ''} {customer.apellido_2 or ''}".strip(),
            "login": customer.email,
            "partner_id": customer.id,
            "website_id": customer.sitio_web_id,
            # Portal group: normalmente se obtiene buscando el grupo 'Portal' en res.groups
            "groups_id": [[6, 0, [2]]],
        }

        return_id = call_odoo(self.endpoint, "object", "execute_kw",
                self.db_odoo, self.uid, self.password_odoo,
                'res.users', 'create', [payload]
            )
        
        print (return_id)

            

    def _send_address(self, customer_id, address: CoreCustomerAddress) -> CoreCustomerAddress:

        tipo_map = {
            CustomerAdressTypes.INVOICE: "invoice",
            CustomerAdressTypes.SHIPPING: "delivery",
            CustomerAdressTypes.CONTACT: "contact",
            CustomerAdressTypes.MAIN: "other"
        }
        payload = {
            "name": address.nombre,
            "type": tipo_map.get(address.tipo_direccion, "other"),
            "street": address.direccion_1,
            "zip": address.cp,
            "city": address.localidad,
            "state_id": None,   # aquí mapearías provincia -> ID de res.country.state
            "country_id": None, # aquí mapearías pais -> ID de res.country
            "phone": address.telefono,
            "parent_id": customer_id
        }
        return_id = call_odoo(self.endpoint, "object", "execute_kw",
                self.db_odoo, self.uid, self.password_odoo,
                'res.partner', 'create', [payload]
            )
        
        address.id = return_id
        return address
        

    def _send_loyalty(self, customer_id, loyalty: CoreCustomersLoyalty) -> CoreCustomersLoyalty:
        payload = {
            "program_id":int(loyalty.programa),   # aquí mapearías programa -> ID de loyalty.program
            "partner_id": customer_id,
            "points": loyalty.puntos
        }

        return_id = call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'loyalty.card', 'create', [payload]
        )

        loyalty.id = return_id
        return loyalty
    
    def _send_invoice(self, customer_id, invoice: CoreCustomerInvoice):


        # tac = call_odoo(self.endpoint, "object", "execute_kw",
        #     self.db_odoo, self.uid, self.password_odoo,
        #     'account.payment.method.line', 'search_read', [[["journal_id", ">", 2]]],
        #     {"fields": ["id", "name","journal_id"]}
        #     )
        
        # print(tac)
        # exit()

        lineas = []
        for linea in invoice.lineas:
            detalle = [0, 0, {
                "product_id": linea.producto_id,        # ID del producto en Odoo
                "name": linea.nombre_articulo,
                "quantity": linea.cantidad,
                "price_unit": linea.precio_unitario,
                "tax_ids": [[6, 0, [linea.impuesto_id]]]  # ID del impuesto configurado en Odoo

                # Odoo calcula subtotal automáticamente
            }]
            lineas.append(detalle)

        payload = {
                    "move_type": "out_invoice",                      # Factura de cliente
                    "name": "/", # invoice.nombre,                          # Número o nombre de factura
                    "invoice_date": invoice.fecha,
                    "invoice_date_due": invoice.fecha,
                    "partner_id": customer_id,                        # Cliente asociado
                    "payment_reference": invoice.referencia_pago,    # Referencia de pago/pedido
                    "invoice_line_ids": lineas,
                    # "amount_untaxed": invoice.cantidad_sin_impuestos,
                    # "amount_total": invoice.cantidad_total,
                }

        factura_id = call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'account.move', 'create', [payload]
        )

        call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'account.move', 'action_post', [factura_id]
        )

        pago = [[{
            "amount":invoice.cantidad_total,
            "payment_date": invoice.fecha,
            "journal_id": 6,
            "payment_method_line_id": 1,
            "communication": "Pago histórico",
            "partner_id": customer_id,
            "payment_type": "inbound"
            }]]




        id_wiazrd_pago = call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'account.payment.register', 'create', pago
        )

        call_odoo(self.endpoint, "object", "execute_kw",
            self.db_odoo, self.uid, self.password_odoo,
            'account.payment.register', 'action_create_payments', id_wiazrd_pago
        )

        invoice.id = factura_id
        return invoice

