"""
登录模块测试用例
"""
import pytest
from loguru import logger
from pages.web.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.web
class TestLogin:
    """登录功能测试"""

    def test_login_with_valid_credentials(self, page):
        """测试用正确账号密码登录"""
        login_page = LoginPage(page)

        # 导航到登录页
        login_page.navigate_to_login()

        # 执行登录
        login_page.login("13260630892", "Aa123456")

        # 如果出现组织选择弹窗，选择第一个组织
        login_page.select_org_if_visible()

        # 等待登录成功 - 使用更宽松的URL匹配
        login_page.wait_for_login_success()

        # 验证登录成功 - SPA应用登录后URL可能保持不变，检查页面内容
        current_url = page.url
        logger.info(f"登录后URL: {current_url}")
        
        # 如果URL仍然包含/login，检查是否存在组织列表（说明已登录但还在选择组织阶段）
        if "/login" in current_url:
            # 检查是否存在主页面元素或组织选择页面
            has_org_list = page.locator('.tenant-item').count() > 0
            if has_org_list:
                # 选择第一个组织
                page.click('.tenant-item', force=True)
                # 等待页面变化
                page.wait_for_load_state("networkidle")
        
        # 最终验证
        current_url = page.url
        logger.info(f"最终URL: {current_url}")
        assert "/login" not in current_url or page.title() != "疆煤宝贸易管理平台-登录", \
            f"登录失败，仍然在登录页: {current_url}"

    def test_login_with_empty_username(self, page):
        """测试空用户名登录"""
        login_page = LoginPage(page)

        # 导航到登录页
        login_page.navigate_to_login()

        # 不填写用户名，直接点击登录
        login_page.click_login()

        # 验证页面仍然在登录页
        assert "/login" in page.url

    def test_login_with_empty_password(self, page):
        """测试空密码登录"""
        login_page = LoginPage(page)

        # 导航到登录页
        login_page.navigate_to_login()

        # 填写用户名，不填写密码
        login_page.fill_username("13260630892")
        login_page.click_login()

        # 验证页面仍然在登录页
        assert "/login" in page.url

    def test_login_with_wrong_password(self, page):
        """测试错误密码登录"""
        login_page = LoginPage(page)

        # 导航到登录页
        login_page.navigate_to_login()

        # 填写错误密码
        login_page.login("13260630892", "wrongpassword")

        # 验证错误提示出现（如果有）
        error_msg = login_page.get_error_message()
        logger.info(f"错误密码测试 - 错误信息: {error_msg}")
        
        # 如果有错误提示，验证内容
        if error_msg:
            assert "密码" in error_msg or "账号" in error_msg or "错误" in error_msg
        
        # 验证仍然在登录页
        assert "/login" in page.url
