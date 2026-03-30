import pytest
from playwright.sync_api import Page, BrowserContext,expect
from pages.login_page import LoginPage
from pages.home_page import HomePage
from config.settings import SETTINGS
import os
import allure

from config.config import CONFIG_TRACE
from utils.logger_handler import logger

AUTH_STATE_PATH = os.getenv("AUTH_STATE_PATH", "auth/.auth.json")

# 把登录逻辑提取成conftest的私有方法
def do_login(page):
    login_page = LoginPage(page)
    login_page.goto(SETTINGS["base_url"])
    login_page.navToLogin()
    login_page.verifyLoginPageLoad()
    login_page.login(SETTINGS["username"], SETTINGS["password"])
    login_page.verifyLogin()

# 完整的登录流程，用来获取session
"""
pytest-playwright 的限制：page 和 context 默认是 function scope，
不能被 session scope 的 fixture 直接使用。
所以 setup_auth 需要自己创建临时浏览器，用完就关
"""
@pytest.fixture(scope="session")
def setup_auth(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    do_login(page)
    
    # 调用context保存函数
    context.storage_state(path=AUTH_STATE_PATH)
    browser.close()

@pytest.fixture
def home_page(page:Page):
    page.goto(SETTINGS["base_url"])
    return HomePage(page)

@pytest.fixture(scope="function",autouse=True)
def ensure_logged_in(page:Page,setup_auth):
    page.goto(SETTINGS["base_url"])
    if "login" in page.url:
        # 重新登录
        do_login(page)
        # 更新auth.json
        page.context.storage_state(path=AUTH_STATE_PATH)
    yield # ← pytest 在这里暂停，先去跑测试 不加的话 homepage也有一个goto 会多开一个tab

# @pytest.fixture
# def do_login(page: Page):
#     """
#     登录函数，并返回已登录Page
#     """
#     login_page = LoginPage(page)
#     login_page.goto(SETTINGS["base_url"])
#     login_page.navToLogin()
    
#     # selenium 风格写法：调用的方法返回bool类型的值，再用if/else判断
#     # if login_page.verifyLoginPageLoad():
#     #     login_page.login(SETTINGS["username"], SETTINGS["password"])

#     # playwright的写法：直接调用-> 静默通过 or raise except
    
#     login_page.verifyLoginPageLoad() # 方法中已经有expect() 了 所以这里直接调用就好
#     login_page.login(SETTINGS["username"], SETTINGS["password"])
    
#     # if login_page.verifyLogin():
#     #     return page
#     # else:
#     #     raise Exception("登录失败")

#     login_page.verifyLogin()
    
#     return page

# -------------------------------------------------------
# 1. 自动 Fixture: 在用例开始前启动 Tracing
# ------------------------------------------------------

# 要匹配 context 的scope 所以需要funtion
@pytest.fixture(scope="function", autouse=True)
def start_tracing(context: BrowserContext):
    """
    全局自动启用 Tracing。
    screenshots=True: 抓取每一帧的截图
    snapshots=True: 抓取 DOM 快照 (这是回放的关键)
    sources=True: 抓取源码
    """
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield


# 定义你的证据保存目录
EVIDENCE_PATH = "./evidence"

# 确保目录存在
if not os.path.exists(EVIDENCE_PATH):
    os.makedirs(EVIDENCE_PATH)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args,setup_auth):
    """
    配置浏览器上下文参数
    """
    return {
        **browser_context_args,
        # 让所有测试自动加载auth.json
        "storage_state":AUTH_STATE_PATH,
        # 1. 开启视频录制，指定临时存放路径
        # 注意：这里先放到 evidence，后续在 hook 里改名
        "record_video_dir": EVIDENCE_PATH,
        # 2. 设置视窗大小 (可选，为了视频清晰度)
        "viewport": {"width": 1280, "height": 720}
    }

# -------------------------------------------------------
# 2. Hook 函数: 捕获失败，截图 + 保存 Trace 并上传 Allure
# -------------------------------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # 只处理测试执行阶段 (call)
    if rep.when == "call":
        # 获取 page 对象
        page = item.funcargs.get("page")
        if not page:
            return

        # 定义基础文件名 (例如: test_login_failure)
        base_name = item.name

        # --- 1. 失败处理逻辑 ---
        if rep.failed:
            # A. 截图 (保存到本地 evidence 目录)
            screenshot_path = os.path.join(EVIDENCE_PATH, f"{base_name}_screenshot.png")
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                # 挂载到 Allure
                allure.attach.file(
                    screenshot_path,
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"截图失败: {e}")

            # B. Trace (保存到本地 evidence 目录)
            trace_path = os.path.join(EVIDENCE_PATH, f"{base_name}_trace.zip")
            try:
                page.context.tracing.stop(path=trace_path)
                # 挂载到 Allure
                allure.attach.file(
                    trace_path,
                    name="Trace链路追踪",
                    attachment_type=allure.attachment_type.ZIP,
                    extension=".zip"
                )
            except Exception as e:
                print(f"Trace 保存失败: {e}")
            
            # C. 视频 (保留并改名)
            # 视频文件是 Playwright 自动生成的，我们需要找到它并改名
            video = page.video
            if video:
                # 等待视频文件写入完成 (稍微有点 trick，通常 page 关闭后才完全写入，
                # 但在这里我们只能先拿到路径，稍后由 Playwright 自动关闭)
                # 更好的方式是直接保存为新路径（Playwright 会负责复制/移动）
                video_path = os.path.join(EVIDENCE_PATH, f"{base_name}_video.webm")
                try:
                    # 必须先关闭 Context 才能确保视频文件完整生成并可被 save_as 操作
                    # 注意：这可能会影响后续依赖 Context 的 teardown 操作，需确保 teardown 具有容错性
                    try:
                        page.context.close()
                    except:
                        pass
                        
                    # save_as 会把当前的视频流保存到指定路径
                    video.save_as(path=video_path)
                    
                    # 删除原始的 hash 命名的视频文件，避免重复
                    try:
                        video.delete()
                    except:
                        pass
                    
                    # 挂载到 Allure
                    allure.attach.file(
                        video_path,
                        name="失败录屏",
                        attachment_type=allure.attachment_type.WEBM
                    )
                except Exception as e:
                    print(f"视频保存失败: {e}")

        # --- 2. 成功处理逻辑 (清理) ---
        else:
            # 如果测试通过，我们需要停止 Tracing 以释放内存，但不保存文件
            try:
                page.context.tracing.stop()
            except:
                pass
            
            # 视频清理策略：
            # 如果你不想保留成功的视频，可以在这里删除。
            # 获取 video 对象
            video = page.video
            if video:
                try:
                    # 必须先关闭 Context 才能确保视频文件完整生成，然后才能删除
                    try:
                        page.context.close()
                    except:
                        pass
                    
                    # 删除生成的视频文件
                    video.delete()
                except Exception as e:
                    print(f"视频删除失败: {e}")
