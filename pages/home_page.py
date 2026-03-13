import allure
from pages.base_page import BasePage
from playwright.sync_api import Page,expect
from utils.logger_handler import logger

class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.homeLoad = page.get_by_text("欢迎来到天天生鲜!")
        self.strawberry = page.get_by_role("link", name="牛奶草莓")
    
    # 同理：selenium风格写法，playwright最好使用expect()
    # def verifyHomePageLoad(self) -> bool:
        
    #     with allure.step("验证首页加载"):
    #         return self.homeLoad.is_visible()

    def verifyHomePageLoad(self):
        with allure.step("验证首页加载"):
            expect(self.homeLoad).to_be_visible()
    
    def pick_Product(self):
        with allure.step("点击产品"):
            self.strawberry.click()
    
    