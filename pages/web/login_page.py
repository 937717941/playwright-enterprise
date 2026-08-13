"""
登录页面对象
"""
from loguru import logger
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
    ORG_CONFIRM_BUTTON = '.el-dialog__footer button:has-text("确定")'

    # 错误提示
    ERROR_MESSAGE = '.el-message--error'
    FORM_ERROR = '.el-form-item__error'

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
        from configs.settings import settings
        
        self.fill_username(username)
        self.fill_password(password)
        self.click_login()
        
        logger.info(f"登录请求已发送，等待响应...")
        
        if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
            error_msg = self.get_text(self.ERROR_MESSAGE)
            logger.error(f"登录失败，错误信息: {error_msg}")
            raise Exception(f"登录失败: {error_msg}")
        
        if self.is_visible(self.FORM_ERROR, timeout=2000):
            error_msg = self.get_text(self.FORM_ERROR)
            logger.error(f"表单验证失败: {error_msg}")
            raise Exception(f"表单验证失败: {error_msg}")
        
        return self

    def select_org_if_visible(self) -> "LoginPage":
        """如果出现组织选择弹窗或组织选择页面，选择第一个组织"""
        from configs.settings import settings
        
        logger.info("检查是否出现组织选择弹窗...")
        
        if self.is_visible(self.ORG_DIALOG, timeout=5000):
            logger.info("检测到组织选择弹窗，选择第一个组织")
            self.click(self.ORG_ITEM)
            
            if self.is_visible(self.ORG_CONFIRM_BUTTON, timeout=3000):
                logger.info("点击确定按钮")
                self.click(self.ORG_CONFIRM_BUTTON)
            
            logger.info("等待跳转到主页面...")
            self.page.wait_for_url(f"{settings.base_url}/**", timeout=60000)
        else:
            org_item_selector = '.tenant-item'
            if self.is_visible(org_item_selector, timeout=3000):
                logger.info("检测到组织选择页面(SPA)，选择第一个组织")
                
                # 使用 expect_navigation 等待导航
                with self.page.expect_navigation(timeout=60000):
                    self.click(org_item_selector)
                
                logger.info("导航完成！")
        
        return self

    def wait_for_login_success(self, timeout: int = 60000) -> "LoginPage":
        """等待登录成功（支持SPA单页应用）"""
        from configs.settings import settings
        
        logger.info(f"等待登录成功，当前URL: {self.get_current_url()}")
        
        try:
            current_url = self.get_current_url()
            
            if "/login" in current_url:
                logger.info("仍在登录页，等待页面跳转...")
                self.page.wait_for_url(f"{settings.base_url}/**", timeout=timeout)
            else:
                logger.info("已离开登录页，等待页面加载完成...")
                self.page.wait_for_load_state("networkidle")
            
            logger.info(f"登录成功！当前URL: {self.get_current_url()}")
        except Exception as e:
            logger.error(f"登录超时，当前URL: {self.get_current_url()}")
            logger.error(f"页面标题: {self.get_title()}")
            raise
        
        return self

    def get_error_message(self) -> str:
        """获取错误提示信息"""
        if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
            return self.get_text(self.ERROR_MESSAGE)
        if self.is_visible(self.FORM_ERROR, timeout=2000):
            return self.get_text(self.FORM_ERROR)
        return ""

    def is_login_button_disabled(self) -> bool:
        """检查登录按钮是否禁用"""
        return self.is_disabled(self.LOGIN_BUTTON)
