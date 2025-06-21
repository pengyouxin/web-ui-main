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


class ProcessRecorder:
    def __init__(self):
        self.driver = None
        self.actions = []

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

    def start_recording(self) -> List[Dict[str, Any]]:
        """开始记录用户在浏览器中的操作"""
        self.start_browser()

        print("浏览器已启动，请进行操作。完成后关闭浏览器窗口以保存记录...")

        # 设置默认初始网址为百度
        initial_url = "https://www.baidu.com/index.htm"
        self._record_action("navigate", "", initial_url)
        self.driver.get(initial_url)

        # 注入 JavaScript 事件监听器来记录点击、滚轮和输入事件
        event_listener_script = """
        document.addEventListener('click', function(event) {
            var xpath = getXPath(event.target);
            var text = event.target.textContent.trim();
            var className = event.target.className;
            var id = event.target.id;
            window.clickInfo = {
                xpath: xpath,
                text: text,
                className: className,
                id: id
            };
        });

        document.addEventListener('wheel', function(event) {
            var xpath = getXPath(event.target);
            window.wheelXPath = xpath;
            window.wheelDeltaY = event.deltaY;
        });

        document.addEventListener('input', function(event) {
            var xpath = getXPath(event.target);
            window.inputXPath = xpath;
            window.inputValue = event.target.value;
        });

        function getXPath(element) {
            if (element.id!== '') {
                return '//*[@id="' + element.id + '"]';
            }
            if (element === document.body) {
                return '//' + element.tagName.toLowerCase();
            }
            var ix = 0;
            var siblings = element.parentNode.childNodes;
            for (var i = 0; i < siblings.length; i++) {
                var sibling = siblings[i];
                if (sibling === element) {
                    var classAttr = element.getAttribute('class');
                    if (classAttr) {
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[@class="' + classAttr + '"][(' + (ix + 1) + ')]';
                    }
                    return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
        }
        """

        self.driver.execute_script(event_listener_script)

        # 记录初始窗口句柄
        initial_window_handle = self.driver.current_window_handle
        all_window_handles = set([initial_window_handle])

        # 开始监控浏览器操作
        last_url = initial_url
        wait_time = 0.5  # 检查间隔时间

        try:
            while True:
                # 检查是否有新窗口打开
                current_window_handles = set(self.driver.window_handles)
                new_window_handles = current_window_handles - all_window_handles
                for new_window_handle in new_window_handles:
                    self.driver.switch_to.window(new_window_handle)
                    self.driver.execute_script(event_listener_script)
                    all_window_handles.add(new_window_handle)

                # 检查是否有新元素加载
                if self._has_new_elements():
                    self.driver.execute_script(event_listener_script)

                # 切换到当前活动窗口
                if self.driver.current_window_handle not in all_window_handles:
                    for handle in all_window_handles:
                        try:
                            self.driver.switch_to.window(handle)
                            break
                        except:
                            continue

                # 检查当前URL是否变化
                current_url = self.driver.current_url
                if current_url != last_url:
                    self._record_action("navigate", "", current_url)
                    last_url = current_url

                # 检查是否有点击事件
                click_info = self.driver.execute_script("return window.clickInfo;")
                if click_info and click_info["xpath"]:
                    self._record_action("click", click_info["xpath"], "",
                                        text=click_info["text"],
                                        class_name=click_info["className"],
                                        element_id=click_info["id"])
                    self.driver.execute_script("window.clickInfo = null;")

                # 检查是否有滚轮事件
                wheel_xpath = self.driver.execute_script("return window.wheelXPath;")
                wheel_delta_y = self.driver.execute_script("return window.wheelDeltaY;")
                if wheel_xpath and wheel_delta_y:
                    self._record_action("wheel", wheel_xpath, str(wheel_delta_y))
                    self.driver.execute_script("window.wheelXPath = null; window.wheelDeltaY = null;")

                # 检查是否有输入事件
                input_xpath = self.driver.execute_script("return window.inputXPath;")
                input_value = self.driver.execute_script("return window.inputValue;")
                if input_xpath and input_value:
                    self._record_action("input", input_xpath, input_value)
                    self.driver.execute_script("window.inputXPath = null; window.inputValue = null;")

                time.sleep(wait_time)

        except Exception as e:
            # 当浏览器窗口关闭时会抛出异常
            print(f"记录完成: {e}")

        finally:
            if self.driver:
                self.driver.quit()

        return self.actions

    def _has_new_elements(self):
        """检查是否有新元素加载"""
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*')))
            return True
        except:
            return False

    def _record_action(self, action_type, selector, value, text="", class_name="", element_id=""):
        """记录操作，添加更多元素信息用于定位"""
        action = {
            "action": action_type,
            "selector": selector,
            "value": value,
            "text": text,
            "class_name": class_name,
            "id": element_id
        }
        self.actions.append(action)