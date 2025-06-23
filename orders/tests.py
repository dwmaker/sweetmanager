from django.test import TestCase
from orders.services import loadxls_order_service
from datetime import datetime


class ServiceTest(TestCase):

    def test_loadxls_order_service(self):

        import pandas as pd
        from orders.models import ExternalProduct
        from products.models import Product, Flavor, Category

        category_bolo = Category.objects.create(name="bolo")

        bento_cake = Product.objects.create(category=category_bolo)

        flavor_cenoura = Flavor.objects.create(category=category_bolo, name="Cenoura")

        ExternalProduct.objects.create(
            ext_product_code="Bentô Cake | 2 fatias",
            ext_addon_code="Sabor Bentô Cake",
            ext_selection_code="Cenoura: Massa de Cenoura com recheio de brigadeiro de chocolate",
            product=bento_cake,
            flavor=flavor_cenoura,
        )

        data = [
            {
                "Id do pedido": 107654119,
                "Número do pedido": "2345678",
                "Cliente": "Iolanda Favero",
                "Status": "Em preparação",
                "Data do agendamento": datetime(year=2025, month=6, day=10),
                "Produtos": """
2.0 x Bentô Cake | 2 fatias 
  Escolha a cobertura:
    1.0 x Cobertura Merengue Buttercream Natural 
  Sabor Bentô Cake:
    1.0 x Cenoura: Massa de Cenoura com recheio de brigadeiro de chocolate 
  Hora de decorar seu Bentô Cake:
    1.0 x Frase a mão livre 
    1.0 x Flork + escrita 
    1.0 x Coração com ou sem frase 
  Escolha como quer embalar seu bentô cake:
    1.0 x Marmitinha Biodegradável 
  📍RETIRADAS (não fazemos entregas):
    1.0 x 🚕 Retirada via aplicativos CARRO 
  ⚠️ LEIA COM ATENÇÃO ⚠️:
    1.0 x ESTOU DE ACORDO 
    1.0 x SOU RESPONSÁVEL PELA RETIRADA DO BOLO 
    1.0 x LI E ACEITO A POLÍTICA DE CANCELAMENTO  
  ⚠️ ESTOU CIENTE QUE::
    1.0 x Preciso enviar a foto de referência da decoração para o whatsapp da loja e descrever ela nas observações abaixo 

""",
            },
        ]

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
        print(df)

        data = loadxls_order_service(df)
        from orders.models import Order, OrderItem, OrderItemFlavor

        order = Order.objects.filter(customer_name="Iolanda Favero").first()
        self.assertIsNotNone(order)
        order_item = OrderItem.objects.filter(
            order=order, product=bento_cake, quantity=2.0
        ).first()
        self.assertIsNotNone(order_item)
        order_item_flavor = OrderItemFlavor.objects.filter(
            order_item=order_item, flavor=flavor_cenoura
        ).first()
        self.assertIsNotNone(order_item_flavor)
