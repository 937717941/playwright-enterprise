"""
基础页面类
封装通用的页面操作方法
"""
import re
import time
from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout
from loguru import logger


class BasePage:
    """基础页面类，封装通用操作"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000  # 默认超时30秒

    def navigate(self, url: str) -> "BasePage":
        """导航到指定URL"""
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def navigate_with_full_load(self, url: str) -> "BasePage":
        """导航到指定URL，等待完全加载"""
        logger.info(f"导航到(完全加载): {url}")
        self.page.goto(url, wait_until="networkidle")
        return self

    def click(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """点击元素"""
        timeout = timeout or self.timeout
        self.page.click(selector, timeout=timeout)
        logger.debug(f"点击: {selector}")
        return self

    def click_force(self, selector: str) -> "BasePage":
        """强制点击（不等待可点击状态）"""
        self.page.click(selector, force=True)
        logger.debug(f"强制点击: {selector}")
        return self

    def double_click(self, selector: str) -> "BasePage":
        """双击元素"""
        self.page.dblclick(selector)
        logger.debug(f"双击: {selector}")
        return self

    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> "BasePage":
        """填写输入框"""
        timeout = timeout or self.timeout
        self.page.fill(selector, value, timeout=timeout)
        logger.debug(f"填写 {selector}: {value}")
        return self

    def type_text(self, selector: str, text: str, delay: int = 50) -> "BasePage":
        """逐字输入"""
        self.page.type(selector, text, delay=delay)
        logger.debug(f"逐字输入 {selector}: {text}")
        return self

    def clear_and_fill(self, selector: str, value: str) -> "BasePage":
        """清空并填写"""
        self.page.click(selector)
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Backspace")
        self.page.fill(selector, value)
        return self

    def select_option(self, selector: str, value: str, timeout: Optional[int] = None) -> "BasePage":
        """选择下拉选项"""
        timeout = timeout or self.timeout
        self.page.select_option(selector, value, timeout=timeout)
        logger.debug(f"选择 {selector}: {value}")
        return self

    def check(self, selector: str) -> "BasePage":
        """勾选复选框"""
        self.page.check(selector)
        logger.debug(f"勾选: {selector}")
        return self

    def uncheck(self, selector: str) -> "BasePage":
        """取消勾选复选框"""
        self.page.uncheck(selector)
        logger.debug(f"取消勾选: {selector}")
        return self

    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """获取元素文本"""
        timeout = timeout or self.timeout
        return self.page.text_content(selector, timeout=timeout) or ""

    def get_inner_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """获取元素内部文本"""
        timeout = timeout or self.timeout
        return self.page.inner_text(selector, timeout=timeout) or ""

    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """获取元素属性"""
        timeout = timeout or self.timeout
        return self.page.get_attribute(selector, attribute, timeout=timeout)

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """检查元素是否可见"""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except PlaywrightTimeout:
            return False

    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """检查元素是否隐藏"""
        try:
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
            return True
        except PlaywrightTimeout:
            return False

    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用"""
        return self.page.is_enabled(selector)

    def is_disabled(self, selector: str) -> bool:
        """检查元素是否禁用"""
        return self.page.is_disabled(selector)

    def wait_for_load_state(self, state: str = "load") -> "BasePage":
        """等待页面加载状态"""
        self.page.wait_for_load_state(state)
        return self

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> "BasePage":
        """等待URL匹配"""
        timeout = timeout or self.timeout
        self.page.wait_for_url(url_pattern, timeout=timeout)
        return self

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> Locator:
        """等待元素"""
        timeout = timeout or self.timeout
        return self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def wait_for_text(self, text: str, timeout: int = 30000) -> "BasePage":
        """等待文本出现"""
        self.page.wait_for_selector(f"text={text}", timeout=timeout)
        return self

    def wait_for_response(self, url_pattern: str, timeout: int = 30000) -> dict:
        """等待响应"""
        with self.page.expect_response(url_pattern, timeout=timeout) as response_info:
            pass
        return response_info.value

    def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> bytes:
        """页面截图"""
        if path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/screenshot_{timestamp}.png"

        # 确保目录存在
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        self.page.screenshot(path=path, full_page=full_page)
        logger.info(f"截图保存: {path}")
        return path

    def get_current_url(self) -> str:
        """获取当前URL"""
        return self.page.url

    def get_title(self) -> str:
        """获取页面标题"""
        return self.page.title()

    def reload(self) -> "BasePage":
        """刷新页面"""
        self.page.reload(wait_until="domcontentloaded")
        return self

    def go_back(self) -> "BasePage":
        """返回上一页"""
        self.page.go_back(wait_until="domcontentloaded")
        return self

    def go_forward(self) -> "BasePage":
        """前进一页"""
        self.page.go_forward(wait_until="domcontentloaded")
        return self

    def press_key(self, selector: str, key: str) -> "BasePage":
        """按键"""
        self.page.press(selector, key)
        return self

    def hover(self, selector: str) -> "BasePage":
        """悬停"""
        self.page.hover(selector)
        return self

    def scroll_to_element(self, selector: str) -> "BasePage":
        """滚动到元素"""
        element = self.page.locator(selector)
        element.scroll_into_view_if_needed()
        return self

    def scroll_to_top(self) -> "BasePage":
        """滚动到顶部"""
        self.page.evaluate("window.scrollTo(0, 0)")
        return self

    def scroll_to_bottom(self) -> "BasePage":
        """滚动到底部"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return self

    def get_page_source(self) -> str:
        """获取页面源码"""
        return self.page.content()

    def evaluate(self, expression: str):
        """执行JavaScript"""
        return self.page.evaluate(expression)

    def dismiss_dialog(self) -> "BasePage":
        """关闭弹窗"""
        self.page.on("dialog", lambda dialog: dialog.dismiss())
        return self

    def accept_dialog(self, prompt_text: Optional[str] = None) -> "BasePage":
        """接受弹窗"""
        if prompt_text:
            self.page.on("dialog", lambda dialog: dialog.accept(prompt_text))
        else:
            self.page.on("dialog", lambda dialog: dialog.accept())
        return self

    def upload_file(self, selector: str, file_path: str) -> "BasePage":
        """上传文件"""
        self.page.set_input_files(selector, file_path)
        return self

    def get_table_data(self, table_selector: str) -> list:
        """获取表格数据"""
        rows = self.page.query_selector_all(f"{table_selector} tr")
        data = []
        for row in rows:
            cells = row.query_selector_all("td")
            if cells:
                row_data = [cell.inner_text() for cell in cells]
                data.append(row_data)
        return data

    def count_elements(self, selector: str) -> int:
        """统计元素数量"""
        return len(self.page.query_selector_all(selector))

    def get_all_text(self, selector: str) -> list:
        """获取所有匹配元素的文本"""
        elements = self.page.query_selector_all(selector)
        return [el.inner_text() for el in elements]
