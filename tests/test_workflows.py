from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
import allure

def test_add_product_to_cart(home_page:HomePage,page: Page):
    product_detail_page = ProductDetailPage(page)
    cart_page = CartPage(page)
    
    with allure.step("Pick product"):
        home_page.verifyHomePageLoad()
        home_page.pick_Product()

    with allure.step("Add product to cart"):
        product_detail_page.verifyProductDetailPageLoad()
        product_detail_page.add_To_Cart()

    with allure.step("Navigate to cart page"):
        #product_detail_page.nav_To_Cart()
        cart_page.verifyCartPageLoad()
    
        cart_page.verify_Product_In_Cart()