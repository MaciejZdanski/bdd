import os
import sys
import pytest
from flask import json
from pytest_bdd import scenarios, given, when, then, parsers

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

scenarios('features/product_management.feature')

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def custom_context():
    class Context:
        pass
    return Context()

@pytest.fixture
@given('I have new product data', target_fixture="new_product_data")
def new_product_data():
    return {"name": "New Product 1", "price": 11.20, "description": "New Product 1", "stock": 3, "status": "Available"}

@pytest.fixture
@given('I have new product data with negative price', target_fixture="new_product_data_with_negative_price")
def new_product_data_with_negative_price():
    return {"name": "Invalid Product", "price": -1.99, "description": "A product with invalid price", "stock": 5, "status": "Available"}

@pytest.fixture
@given('I have a product')
def i_have_a_product(custom_context, client):
    product_data = {"name": "Test Product", "price": 25.00, "description": "Test product", "stock": 10,"status": "Available"}
    response = client.post('/product', json=product_data)
    product_id = response.get_json()['id']
    custom_context.product_id = product_id 
    return product_id


@when("I add the product")
def add_product(custom_context, client, new_product_data):
    custom_context.response = client.post('/product', json=new_product_data)
    

@when("I add the product with negative price")
def add_product_with_negative_price(custom_context, client, new_product_data_with_negative_price):
    custom_context.response = client.post('/product', json=new_product_data_with_negative_price)
    

@when('I update the product stock to 0')
def update_product_stock_to_zero(custom_context, client, i_have_a_product):
    product_id = i_have_a_product
    update_data = {"stock": 0}
    custom_context.response = client.put(f'/product/{product_id}', json=update_data)
    custom_context.product_id = product_id  # Store product ID for later use
    
    
@pytest.fixture
@when('I update the product')
def update_product(custom_context, client, i_have_a_product):
    product_id = i_have_a_product
    update_data = {"description": "Updated product description"}
    client.put(f'/product/{product_id}', json=update_data)
    custom_context.product_id = product_id
    
    
@pytest.fixture
@when('I update the product details')
def update_product_details(custom_context, client, i_have_a_product):
    product_id = i_have_a_product
    update_data = {"description": "Updated description", "price": 30.00}
    custom_context.response = client.put(f'/product/{product_id}', json=update_data)
    custom_context.product_id = product_id
    

@when('I delete the product')
def delete_product(custom_context, client, i_have_a_product):
    product_id = i_have_a_product
    custom_context.response = client.delete(f'/product/{product_id}')


@then(parsers.parse('the response status code should be {code:d}'))
def response_status_code(custom_context, code):
    assert custom_context.response.status_code == code

@then(parsers.parse("the response should contain the product"))
def response_contains_product(custom_context):
    assert "id" in custom_context.response.get_json()
    
@then('the product status should be "Unavailable"')
def product_status_should_be_unavailable(custom_context, client):
    product_id = custom_context.product_id
    response = client.get(f'/product/{product_id}')
    product = response.get_json()
    assert product['status'] == 'Unavailable'

    
@then("the response should indicate a validation error")
def response_indicates_validation_error(custom_context):
    assert custom_context.response.status_code == 400
    response_data = json.loads(custom_context.response.data)
    assert "error" in response_data or "message" in response_data  # 

@then('I should be able to view the history of the product')
def view_product_history(custom_context, client):
    product_id = custom_context.product_id
    response = client.get(f'/product/{product_id}/history')
    history = response.get_json()

    assert response.status_code == 200
    assert len(history) > 0  
    assert 'changes' in history[0] 

@then(parsers.parse('the response status code should be {code:d}'))
def response_status_code_for_update(custom_context, code):
    assert custom_context.response.status_code == code

@then('the product details should be updated')
def product_details_should_be_updated(custom_context, client):
    product_id = custom_context.product_id
    response = client.get(f'/product/{product_id}')
    product = response.get_json()

    assert product['description'] == "Updated description"
    assert product['price'] == 30.00
    
@then(parsers.parse('the response status code should be {code:d}'))
def response_status_code_for_delete(custom_context, code):
    assert custom_context.response.status_code == code

@then('the product should no longer exist')
def product_should_no_longer_exist(custom_context, client):
    product_id = custom_context.product_id
    response = client.get(f'/product/{product_id}')
    assert response.status_code == 404  
