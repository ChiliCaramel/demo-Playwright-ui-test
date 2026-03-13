from pages.base_page import BasePage
from playwright.sync_api import Page,expect
import allure
from utils.logger_handler import logger

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.navToLogin_link = page.get_by_role("link", name="登录")
        self.loginLoad = page.get_by_text("用户登录")
        self.username = page.get_by_placeholder("请输入用户名")
        self.pwd = page.get_by_placeholder("请输入密码")
        self.login_btn = page.get_by_role("button", name="登录")
        self.success_toast = page.get_by_text("Caramel")

    def navToLogin(self):
        with allure.step("导航到登录页面"):
            self.navToLogin_link.click()
    
    def verifyLoginPageLoad(self):
        """这是selenium带来的习惯，直接用is_visible是直接检查，不等待
        当这个locator还在加载，会直接返回false
        seleium中可以这么写是因为一般会在base_page中对selenium基本操作进行封装 封装时会加显示等待操作"""
        ##return self.loginLoad.is_visible()
        expect(self.loginLoad).to_be_visible()

    def login(self, username: str, pwd: str):
        self.username.fill(username)
        self.pwd.fill(pwd)
        self.login_btn.click()
    
    def verifyLogin(self):
        ## 同理
        ##self.success_toast.is_visible()
        expect(self.success_toast).to_be_visible()