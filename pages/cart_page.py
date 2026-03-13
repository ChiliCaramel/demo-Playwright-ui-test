from pages.base_page import BasePage
from playwright.sync_api import Page,expect
from utils.logger_handler import logger

class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.cartLoad = page.locator(".sub_page_name.fl").get_by_text("购物车")
        self.strawberry = page.get_by_text("牛奶草莓")
    
    # def verifyCartPageLoad(self) -> bool:
    #     return self.cartLoad.is_visible()

    def verifyCartPageLoad(self):
        expect(self.cartLoad).to_be_visible()
    
    # def verify_Product_In_Cart(self) -> bool:
    #     logger.info("Verify strawberry is in cart.")
    #     return self.strawberry.is_visible()

    def verify_Product_In_Cart(self):
        logger.info("Verify strawberry is in cart.")
        expect(self.strawberry).to_be_visible()