# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
import base64
import requests

#login credentials to the merchant porta
#https://playground.eu.portal.klarna.com
#username: christian.drago+workshop@klarna.com
#password: ts-workshop


#store credentials. Those should be store in the DB
from ts_workshop.settings import klarna_base_url, my_http_address

store_uid = "PK01709_8099f8375bf8"
store_password = "4AkTf3XLmjg6bGIv"
store_auth = base64.b64encode(store_uid + ":" + store_password)

#static parameters
content_type_value = "application/json"
headers = {'content-type': content_type_value, "Authorization": "Basic %s"%store_auth }



# initialize checkout session
def render_checkout(request):
    checkout_uri = request.GET.get('checkout_uri', None)

    request_body = {
        "purchase_country": "se",
        "purchase_currency": "sek",
        "locale": "sv-se",
        "order_amount": 20000,
        "order_tax_amount": 4000,
        "order_lines": [
            {
                "type": "physical",
                "reference": "19-402-USA",
                "name": "Red T-Shirt",
                "quantity": 2,
                "quantity_unit": "pcs",
                "unit_price": 10000,
                "tax_rate": 2500,
                "total_amount": 20000,
                "total_discount_amount": 0,
                "total_tax_amount": 4000,
                "merchant_data": "{\"marketplace_seller_info\":[{\"product_category\":\"Women's Fashion\",\"product_name\":\"Women Sweatshirt\"}]}",
                "product_url": "https://www.estore.com/products/f2a8d7e34",
                "image_url": "https://www.exampleobjects.com/logo.png",
                "product_identifiers": {
                    "category_path": "Electronics Store > Computers & Tablets > Desktops",
                    "global_trade_item_number": "735858293167",
                    "manufacturer_part_number": "BOXNUC5CPYH",
                    "brand": "Intel"
                }
            }
        ],
        "merchant_urls": {
            "terms": "https://www.estore.com/terms.html",
            "checkout": my_http_address + "/kcov3/render_checkout",
            "confirmation": "https://www.google.com",
            "push": my_http_address + "/kcov3/push?checkout_uri={checkout.order.id}",
            "validation": my_http_address + "/kcov3/validate"
            # "cancellation_terms": "https://www.estore.com/terms/cancellation.html",
            # "shipping_option_update": "https://www.estore.com/api/shipment",
            # "address_update": "https://www.estore.com/api/address",
            # "notification": "https://www.estore.com/api/pending",
            # "country_change": "https://www.estore.com/api/country"
        }
    }

    response = requests.post(klarna_base_url + '/checkout/v3/orders', headers=headers, data=json.dumps(request_body)) #trigger the request

    bring_to_frontend = {}


    if 200 <= response.status_code <= 299: #positive response
        bring_to_frontend['checkout_snippet'] = (response.json())['html_snippet']
        bring_to_frontend['success'] = True

    elif response.status_code == 401:
        bring_to_frontend = {
            'success': False,
            'reason': 'Authentication error'
        }
    elif response.status_code == 400:
        bring_to_frontend = {
            'success': False,
            'reason': 'Malformed request, error in the request body'
        }

    return render(request, 'kcov3/checkout_page.html', bring_to_frontend)

@csrf_exempt
def handle_push_notification(request):
    checkout_uri = request.GET.get('checkout_uri', None)


    order_read_response = requests.get(klarna_base_url + '/ordermanagement/v1/orders/{}'.format(checkout_uri), headers=headers)
    #read order and check it against the database
    ack_order = True

    if ack_order:
        order_ack_response = requests.post(klarna_base_url + '/ordermanagement/v1/orders/{}/acknowledge'.format(checkout_uri), headers=headers)
    else:
        order_cancel_response = requests.post(klarna_base_url + '/ordermanagement/v1/orders/{}/cancel'.format(checkout_uri), headers=headers)

    return HttpResponse(status=200)

@csrf_exempt
def validate_order(request):
    order_valid = False
    if order_valid:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=307)#add the location header!!



