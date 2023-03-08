import os

import requests
from faker import Faker

from allure_commons._allure import step
from selene import have
from selene.support.conditions import be
from selene.support.shared import browser
from dotenv import load_dotenv

from framework.demoqa import DemoQA
from framework.demoqa_with_env import DemoQaWithEnv
from utils.base_session import BaseSession

fake = Faker()


load_dotenv()

API_URL = os.getenv('API_URL')
print(f"API_URL={API_URL}")
WEB_URL = os.getenv("WEB_URL")
print(f"WEB_URL={WEB_URL}")
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')

browser.config.base_url = WEB_URL


def test_login():
    """Successful authorization to some demowebshop (UI)"""
    with step("Open login page"):
        browser.open("/login")

    with step("Fill login form"):
        browser.element("#Email").send_keys(login)
        browser.element("#Password").send_keys(password).press_enter()

    with step("Verify successful authorization"):
        browser.element(".account").should(have.text(login))


def test_login_though_api():
    response = requests.post(f"{API_URL}/login", json={"Email": "demo_webshop@test.com", "Password": "123123"}, allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")

    browser.open("/Themes/DefaultClean/Content/images/logo.png")

    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open("")

    with step("Verify successful authorization"):
        browser.element(".account").should(have.text(login))


def test_login_though_api_with_base_session():
    demoshop = BaseSession(API_URL)
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"}, allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")

    browser.open("/Themes/DefaultClean/Content/images/logo.png")

    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open("")

    with step("Verify successful authorization"):
        browser.element(".account").should(have.text(login))


def test_login_though_api_with_base_session_fixture(demoshop):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"}, allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")

    browser.open("/Themes/DefaultClean/Content/images/logo.png")

    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open("")

    with step("Verify successful authorization"):
        browser.element(".account").should(have.text(login))


def test_check_cart_quantity(demoshop, clean_cart):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"}, allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")
    browser.open("/Themes/DefaultClean/Content/images/logo.png")
    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    demoshop.post('/addproducttocart/catalog/13/1/1')
    demoshop.post('/addproducttocart/catalog/22/1/1')
    demoshop.post('/addproducttocart/catalog/45/1/1')
    browser.open("")
    browser.element('.ico-cart .cart-label').click()
    with step('check cart size'):
        browser.element('.cart-label~.cart-qty').should(have.text('(3)'))


def test_gift_cards_match(demoshop, clean_cart):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"},
                             allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")
    browser.open("/Themes/DefaultClean/Content/images/logo.png")
    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open('https://demowebshop.tricentis.com/gift-cards')
    recipient_info = {
        "name": fake.first_name(),
        "email": fake.email()
    }

    def fill_recipient_info():
        browser.element('.recipient-name').type(recipient_info["name"])
        browser.element(".recipient-email").type(recipient_info["email"])
        browser.element('[id|=add-to-cart-button][type="button"]').click()

    browser.element('.product-title>[href="/25-virtual-gift-card"]').click()
    fill_recipient_info()
    response = demoshop.get('/cart')
    with step('Check recipient info'):
        assert recipient_info['name'], recipient_info['email'] in response.text
        browser.element('.ico-cart .cart-label').click()


def test_books_match(demoshop, clean_cart):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"},
                             allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")
    browser.open("/Themes/DefaultClean/Content/images/logo.png")
    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open('https://demowebshop.tricentis.com/books')
    for book in browser.elements('[type = "button"][value = "Add to cart"]'):
        book.click()
        browser.wait_until(book.should(be.clickable))
    response = demoshop.get('/cart')
    with step('check total price'):
        assert '44.00' in response.text


def test_add_digital_downloads_to_wishlist(demoshop, clean_wishlist):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"},
                             allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")
    browser.open("/Themes/DefaultClean/Content/images/logo.png")
    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    demoshop.post('/addproducttocart/details/53/2')
    demoshop.post('/addproducttocart/details/51/2')
    demoshop.post('/addproducttocart/details/52/2')
    browser.open("")
    browser.element('#topcartlink~li .ico-wishlist').click()
    with step('check wishlist content'):
        browser.element('.share-link').should(be.existing).click()
        browser.all('.product>[href]').should(have.texts('3rd Album', 'Music 2', 'Music 2'))


def test_compare_desktop_pc(demoshop, clear_compare_list):
    response = demoshop.post("/login", json={"Email": "demo_webshop@test.com", "Password": "123123"},
                             allow_redirects=False)
    authorization_cookie = response.cookies.get("NOPCOMMERCE.AUTH")
    browser.open("/Themes/DefaultClean/Content/images/logo.png")
    browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": authorization_cookie})
    browser.open('https://demowebshop.tricentis.com/desktops')
    browser.element('.product-title>[href="/build-your-cheap-own-computer"]').click()
    browser.element('[type="radio"][value="65"]').click()
    browser.element('[type="radio"][value="55"]').click()
    browser.element('[type="radio"][value="58"]').click()
    browser.element('[type="checkbox"][value="94"]').click()
    browser.element('[type = "button"][value="Add to compare list"]').click()
    browser.open('https://demowebshop.tricentis.com/notebooks')
    browser.element('.product-title>[href="/141-inch-laptop"]').click()
    browser.element('[type = "button"][value="Add to compare list"]').click()
    browser.save_screenshot('compare.png')
    with step('check screenshot not empty'):
        assert os.path.getsize('compare.png') != 0
    os.remove('compare.png')


def test_add_one_product_to_cart_authorized(demoshop):
    """Тест с прокидыванием сессии во фреймворк"""
    with step("Авторизоваться"):
        demoqa = DemoQA(demoshop)
        demoqa.authorization_cookie = demoqa.login(email=login, password=password)

    with step("Добавление товара в корзину"):
        result = demoqa.add_to_cart(cookies=demoqa.authorization_cookie)

    with step("Товар добавлен в корзину"):
        assert result.status_code == 200
        assert 'The product has been added to your' in result.json()["message"]


def test_add_one_product_to_cart_authorized_with_env(env):
    """Тест с прокидыванием окружения во фреймворк"""
    with step("Авторизоваться"):
        demoqa = DemoQaWithEnv(env)
        demoqa.authorization_cookie = demoqa.login(email=login, password=password)

    with step("Добавление товара в корзину"):
        result = demoqa.add_to_cart(cookies=demoqa.authorization_cookie)

    with step("Товар добавлен в корзину"):
        assert result.status_code == 200
        assert 'The product has been added to your' in result.json()["message"]













    













