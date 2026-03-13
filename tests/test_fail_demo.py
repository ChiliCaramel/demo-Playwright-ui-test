from playwright.sync_api import Page
from utils.logger_handler import logger
import allure
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage

@allure.feature("Demo")
@allure.story("测试失败用例")
def test_fail_demo(do_login: Page):
    
    with allure.step("Do login."):
        home_page = HomePage(do_login)
        product_detail_page = ProductDetailPage(do_login)
        cart_page = CartPage(do_login)
    
    with allure.step("Pick product."):
        home_page.verifyHomePageLoad()
        home_page.pick_Product()

    with allure.step("Add product to cart."):
        product_detail_page.verifyProductDetailPageLoad()
        product_detail_page.add_To_Cart()

    with allure.step("Verify cart page load."):
        cart_page.verifyCartPageLoad()
    
    with allure.step("Verify if product in the cart."):
        assert cart_page.verify_Product_In_Cart()

def test_fail_for_trace(page):
    page.goto("https://www.google.com")
    # 故意断言失败
    assert page.title() == "Baidu"