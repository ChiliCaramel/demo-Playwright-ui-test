from utils.logger_handler import logger
from pages.base_page import BasePage
from playwright.sync_api import Page,expect

class ProductDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.productLoad = page.locator(".breadcrumb").get_by_text("商品详情")
        self.addToCart = page.get_by_role("button", name="加入购物车").or_(page.get_by_role("link", name="加入购物车"))
        self.navToCart = page.get_by_role("button", name="我的购物车").or_(page.get_by_role("link", name="我的购物车")).first
    
    # def verifyProductDetailPageLoad(self) -> bool:
    #     return self.productLoad.is_visible()

    def verifyProductDetailPageLoad(self):
        expect(self.productLoad).to_be_visible()
    
    def add_To_Cart(self):
        logger.info("add product to cart.")
        self.addToCart.click()
    
    def nav_To_Cart(self):
        logger.info("Navigate to cart from product detail page.")
        self.navToCart.click()
    
    
    
    