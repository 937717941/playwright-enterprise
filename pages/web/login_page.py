"""
登录页面对象
"""
from pages.base.base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""

    # 元素定位器
    USERNAME_INPUT = '[placeholder="请输入账号"]'
    PASSWORD_INPUT = '[placeholder="请输入密码"]'
    LOGIN_BUTTON = 'button:has-text("登 录")'
    FORGOT_PASSWORD_LINK = 'button:has-text("忘记密码")'

    # 组织选择弹窗
    ORG_DIALOG = '.el-dialog'
    ORG_ITEM = '.el-dialog__body >> text=樱华国际贸易'
    ORG_DIALOG_CLOSE = '.el-dialog__headerbtn'

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def navigate_to_login(self) -> "LoginPage":
        """导航到登录页"""
        from configs.settings import settings
        self.navigate(f"{settings.base_url}/login")
        return self

    def fill_username(self, username: str) -> "LoginPage":
        """填写用户名"""
        self.fill(self.USERNAME_INPUT, username)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """填写密码"""
        self.fill(self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "LoginPage":
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON)
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        """执行登录操作"""
        self.fill_username(username)
        self.fill_password(password)
        self.click_login()
        return self

    def select_org_if_visible(self) -> "LoginPage":
        """如果出现组织选择弹窗，选择第一个组织"""
        if self.is_visible(self.ORG_DIALOG, timeout=5000):
            self.click(self.ORG_ITEM)
        return self

    def wait_for_login_success(self, timeout: int = 60000) -> "LoginPage":
        """等待登录成功"""
        from configs.settings import settings
        self.wait_for_url(f"{settings.base_url}/**/target/**", timeout=timeout)
        return self

    def get_error_message(self) -> str:
        """获取错误提示信息"""
        error_selector = ".el-message--error, .el-form-item__error"
        if self.is_visible(error_selector, timeout=3000):
            return self.get_text(error_selector)
        return ""

    def is_login_button_disabled(self) -> bool:
        """检查登录按钮是否禁用"""
        return self.is_disabled(self.LOGIN_BUTTON)
