import time
import os
import tempfile
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class BrowserController:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        edge_options = Options()
        edge_options.add_argument("--start-maximized")
        # 添加稳定性参数
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")

        # 使用临时用户数据目录
        temp_dir = os.path.join(tempfile.gettempdir(), "edge_user_data")
        edge_options.add_argument(f"--user-data-dir={temp_dir}")

        self.driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=edge_options
        )

    def perform_actions(self, actions: List[Dict[str, Any]]):
        """执行记录的操作序列，增加对动态元素的处理"""
        self.start_browser()
        print("执行自动化操作...")

        for action in actions:
            action_type = action.get("action")
            selector = action.get("selector")
            value = action.get("value")
            text = action.get("text", "")
            class_name = action.get("class_name", "")
            element_id = action.get("id", "")

            try:
                # 处理导航
                if action_type == "navigate":
                    url = action.get("url", value)
                    self.driver.get(url)
                    print(f"导航到: {url}")
                    time.sleep(3)  # 等待页面加载

                # 处理点击（增加动态元素处理）
                elif action_type == "click":
                    element = self._find_element_with_retries(selector, text, class_name, element_id)
                    if element:
                        element.click()
                        print(f"点击元素: {selector}")
                        time.sleep(2)
                    else:
                        print(f"无法定位元素: {selector}")

                # 处理输入
                elif action_type == "input":
                    element = self._find_element_with_retries(selector, text, class_name, element_id)
                    if element:
                        element.clear()
                        element.send_keys(value)
                        print(f"在元素中输入: {value}")
                        time.sleep(2)
                    else:
                        print(f"无法定位输入元素: {selector}")

                # 处理滚轮
                elif action_type == "wheel":
                    element = self._find_element_with_retries(selector, text, class_name, element_id)
                    if element:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element).scroll_by_amount(0, int(value)).perform()
                        print(f"在元素上滚动: {value} 个单位")
                        time.sleep(2)
                    else:
                        print(f"无法定位滚动元素: {selector}")

                time.sleep(1)  # 操作间隔

            except Exception as e:
                print(f"执行操作时出错: {e}")
                print(f"操作: {action}")
                print("继续执行后续操作...")

        print("自动化操作执行完成")
        time.sleep(5)  # 等待5秒后关闭浏览器
        if self.driver:
            self.driver.quit()

    def _find_element_with_retries(self, selector, text="", class_name="", element_id=""):
        """尝试多种方法定位元素，提高动态元素的定位成功率"""
        # 方法1：直接使用记录的XPath选择器
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            return element
        except Exception as e:
            print(f"直接定位失败: {e}")

        # 方法2：使用元素文本定位（如果有文本）
        if text:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]"))
                )
                return element
            except Exception as e:
                print(f"通过文本定位失败: {e}")

        # 方法3：使用class名称定位（如果有class）
        if class_name:
            try:
                # 提取第一个稳定的class（排除可能包含动态数字的class）
                stable_class = class_name.split()[0]
                if not any(char.isdigit() for char in stable_class):
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[contains(@class, '{stable_class}')]"))
                    )
                    return element
            except Exception as e:
                print(f"通过class定位失败: {e}")

        # 方法4：使用ID定位（如果有ID）
        if element_id:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, element_id))
                )
                return element
            except Exception as e:
                print(f"通过ID定位失败: {e}")

        # 方法5：使用CSS选择器（尝试转换XPath为CSS）
        try:
            css_selector = self._convert_xpath_to_css(selector)
            if css_selector:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                )
                return element
        except Exception as e:
            print(f"通过CSS选择器定位失败: {e}")

        # 所有方法都失败，返回None
        return None

    def _convert_xpath_to_css(self, xpath):
        """简单地将XPath转换为CSS选择器（有限支持）"""
        try:
            # 移除XPath前缀
            if xpath.startswith("//"):
                xpath = xpath[2:]

            # 处理ID
            xpath = xpath.replace("[@id='", "#").replace("']", "")

            # 处理class
            xpath = xpath.replace("[@class='", ".").replace("']", "")

            # 处理属性
            xpath = xpath.replace("[@", "[").replace("']", "]")

            # 替换斜杠为空格
            xpath = xpath.replace("/", " ")

            return xpath
        except:
            return None