from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from countries_states_cities.models import Country as CountryModel
from .models import Product, Brand, Category, Unit, Price, Warehouse, Stock, Image, Project, Seria

transport = Transport(cache=SqliteCache())
wsdl  = 'http://192.168.0.111/EVYAP_TEST2/EVYAP_TEST2.1cws?wsdl'
settings = Settings(strict=False, xml_huge_tree=True)
# client = Client(wsdl=wsdl, settings=settings, transport=transport)
client = Client(wsdl=wsdl, transport=transport)

def clean(value):
    if not value or value in ["NULL", "None", "null"]:
        return None
    return str(value).strip()

def get_products_from_1c():
    try:
        response = client.service.GetProductList()
        if hasattr(response, 'ProductItem'):
            return response.ProductItem
        elif isinstance(response, list):
            return response
        elif hasattr(response, 'TotalCount'):
            print("TotalCount: ",response.TotalCount)
            return response.TotalCount
        else:
            return []
    except Exception as e:
        print("Error fetching products from 1C:", e)
        # return None

def save_or_update_product(data: dict):
    pass

@api_view(['GET'])
def sync_products_from_1c(request):
    products = get_products_from_1c()
    
    created_count = 0
    updated_count = 0
    
    for item in products:
        product_data = {
            'code': getattr(item, 'Code', None),
            'name': getattr(item, 'Name', None),
            'article': getattr(item, 'Article', None),
            'barcode':getattr(item, 'Shtrix', None),
            'brand_name': getattr(item, 'Brand', None),
            'supplier': getattr(item, 'Suplier', None),
            'category_name': getattr(item, 'Category', None),
            'country_name': getattr(item, 'Country', None),
            'country_code': getattr(item, 'CountryCode', None),
            'unit_name': getattr(item, 'Unit', None),
            'project_name': getattr(item, 'Project', None),
            'series_name': getattr(item, 'Seria', None),
        }

        for key, value in product_data.items():
            if str(value).strip().upper() == 'NULL':
                product_data[key] = None

        brand = category = unit = project = series = country  = None

        if product_data['brand_name']:
            brand, _ = Brand.objects.get_or_create(name=product_data['brand_name'])

        if product_data['category_name']:
            category, _ = Category.objects.get_or_create(name=product_data['category_name'])

        if product_data['unit_name']:
            unit, _ = Unit.objects.get_or_create(name=product_data['unit_name'])
            
        if product_data['project_name']:
            project, _ = Project.objects.get_or_create(name=product_data['project_name'])
            
        if product_data['series_name']:
            series, _ = Seria.objects.get_or_create(name=product_data['series_name'])
        # if product_data['country_name']:
        #     country, _ = CountryModel.objects.get_or_create(
        #         name=product_data['country_name'],
        #         defaults={'code': product_data['country_code']},
        #     )

        obj, created = Product.objects.update_or_create(
            article_number=product_data['article'],
            defaults={
                'nomenclature_code': product_data['code'],
                'name': product_data['name'],
                'brand': brand,
                'category': category,
                'unit': unit,
                'supplier': product_data['supplier'],
                'project': project,
                'series': series,
                'barcode': product_data['barcode'],
                # 'country_of_origin': country,
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1
    return Response({'created': created_count, 'updated': updated_count})
    
    

        
  