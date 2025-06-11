import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

class BrowserController:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        chrome_options = Options()
        # 取消下面注释可以在无头模式下运行
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.maximize_window()

    def start_recording(self) -> List[Dict[str, Any]]:
        """开始记录用户在浏览器中的操作"""
        self.start_browser()
        print("开始记录操作...")
        print("提示: 完成后关闭浏览器窗口以结束记录")

        actions = []

        # 这里需要一个更复杂的机制来实际记录用户操作
        # 简单示例：等待用户关闭浏览器
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("记录已停止")
        except Exception as e:
            print(f"操作记录期间出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        # 在实际应用中，这里应该返回实际记录的操作
        # 为了示例，我们返回一个模拟的操作序列
        return [
            {"action": "navigate", "url": "https://www.example.com"},
            {"action": "click", "selector": "button.login", "by": "CSS_SELECTOR"},
            {"action": "type", "selector": "input.username", "by": "CSS_SELECTOR", "value": "user"},
            {"action": "type", "selector": "input.password", "by": "CSS_SELECTOR", "value": "password"},
            {"action": "click", "selector": "button.submit", "by": "CSS_SELECTOR"}
        ]

    def perform_actions(self, actions: List[Dict[str, Any]]):
        """执行记录的操作序列"""
        self.start_browser()
        print("执行自动化操作...")

        for action in actions:
            # 处理记录的操作（使用'type'键）和模拟操作（使用'action'键）
            action_type = action.get("type", action.get("action"))

            try:
                if action_type == "navigate":
                    url = action.get("url", action.get("value"))
                    self.driver.get(url)
                    print(f"导航到: {url}")
                    # 增加页面加载等待时间
                    time.sleep(3)

                elif action_type == "click":
                    by_str = action.get("by", "CSS_SELECTOR")
                    by = getattr(By, by_str)
                    selector = action.get("selector")
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    element.click()
                    print(f"点击元素: {selector}")
                    # 增加点击后等待时间
                    time.sleep(2)

                elif action_type == "type" or action_type == "input":
                    by_str = action.get("by", "CSS_SELECTOR")
                    by = getattr(By, by_str)
                    selector = action.get("selector")
                    value = action.get("value")
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    element.clear()
                    element.send_keys(value)
                    print(f"在元素中输入: {value}")
                    # 增加输入后等待时间
                    time.sleep(2)

                elif action_type == "wheel":
                    by = By.XPATH
                    selector = action.get("selector")
                    value = int(action.get("value"))
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    actions = ActionChains(self.driver)
                    actions.move_to_element(element).scroll_by_amount(0, value).perform()
                    print(f"在元素 {selector} 上滚动: {value} 个单位")
                    time.sleep(2)

                # 为了演示效果，添加一些延迟
                time.sleep(1)

            except Exception as e:
                print(f"执行操作时出错: {e}")
                print(f"操作: {action}")
                print("继续执行后续操作...")

        print("自动化操作执行完成")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()