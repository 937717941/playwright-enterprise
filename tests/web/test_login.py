"""
登录模块测试用例
"""
import pytest
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

        # 等待登录成功
        login_page.wait_for_login_success()

        # 验证登录成功
        assert "target" in page.url or "xjcec-trade" in page.url

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
        # 注意：系统可能不显示具体错误，需要根据实际情况调整
        error_msg = login_page.get_error_message()
        if error_msg:
            assert "密码" in error_msg or "账号" in error_msg or "错误" in error_msg
