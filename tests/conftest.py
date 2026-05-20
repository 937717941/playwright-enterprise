"""
pytest配置文件
定义全局fixture和钩子
"""
import json
import os
import time
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.settings import settings


# ==================== Session Fixtures ====================

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """浏览器启动参数"""
    launch_args = {
        **browser_type_launch_args,
        "args": [
            "--start-maximized",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }
    return launch_args


# ==================== Function Fixtures ====================

@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    """创建新页面"""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    page = context.new_page()

    # 设置默认超时
    page.set_default_timeout(settings.timeout)

    yield page

    # 测试后清理
    page.close()
    context.close()


@pytest.fixture(scope="function")
def authenticated_page(page: Page) -> Page:
    """已登录的页面（使用storage_state）"""
    auth_file = Path("auth.json")

    if auth_file.exists():
        # 加载已保存的登录状态
        context = page.context
        context.storage_state(path=str(auth_file))
        page.goto(settings.base_url)
    else:
        # 执行登录流程
        page.goto(f"{settings.base_url}/login")
        page.fill('[placeholder="请输入账号"]', settings.admin_username)
        page.fill('[placeholder="请输入密码"]', settings.admin_password)
        page.click('button:has-text("登 录")')
        page.wait_for_url("**/target/**", timeout=60000)

        # 保存登录状态
        page.context.storage_state(path=str(auth_file))

    yield page

    # 不关闭，让其他用例复用登录状态


@pytest.fixture(scope="function")
def mobile_page(browser: Browser) -> Page:
    """移动端H5页面"""
    context = browser.new_context(
        viewport={"width": 375, "height": 812},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        locale="zh-CN",
    )
    page = context.new_page()
    page.set_default_timeout(settings.timeout)

    yield page

    page.close()
    context.close()


# ==================== Data Fixtures ====================

@pytest.fixture(scope="session")
def test_users():
    """加载测试用户数据"""
    users_file = Path(__file__).parent.parent / "data" / "users" / "users.json"
    with open(users_file, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def admin_user(test_users):
    """管理员用户"""
    return test_users["admin"]


# ==================== Hooks ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子 - 失败时截图"""
    outcome = yield
    result = outcome.get_result()

    if result.when == "call" and result.failed:
        page = item.funcargs.get("page")
        if page:
            # 确保截图目录存在
            screenshot_dir = Path(settings.screenshot_dir)
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # 生成截图文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshot_dir / f"{item.name}_{timestamp}.png"

            # 截图
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n截图已保存: {screenshot_path}")

            # 保存页面源码
            html_path = screenshot_dir / f"{item.name}_{timestamp}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"页面源码已保存: {html_path}")


def pytest_configure(config):
    """pytest配置钩子"""
    # 设置环境变量
    os.environ.setdefault("ENVIRONMENT", "dev")


def pytest_collection_modifyitems(config, items):
    """修改收集到的测试用例"""
    for item in items:
        # 自动添加web标记
        if "web" in str(item.fspath):
            item.add_marker(pytest.mark.web)

        # 自动添加mobile标记
        if "mobile" in str(item.fspath):
            item.add_marker(pytest.mark.mobile)


# ==================== Markers ====================

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "web: Web端测试")
    config.addinivalue_line("markers", "mobile: 移动端H5测试")
    config.addinivalue_line("markers", "slow: 执行时间较长的测试")
    config.addinivalue_line("markers", "flaky: 不稳定测试")
