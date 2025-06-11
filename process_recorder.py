import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class ProcessRecorder:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def start_recording(self) -> List[Dict[str, Any]]:
        """开始记录用户在浏览器中的操作"""
        self.actions = []
        self.start_browser()

        print("浏览器已启动，请进行操作。完成后关闭浏览器窗口以保存记录...")

        # 设置默认初始网址为百度
        initial_url = "https://www.baidu.com/index.htm"
        self._record_action("navigate", "", initial_url)
        self.driver.get(initial_url)

        # 注入 JavaScript 事件监听器来记录点击和滚轮事件
        event_listener_script = """
        document.addEventListener('click', function(event) {
            var xpath = getXPath(event.target);
            window.clickXPath = xpath;
        });

        document.addEventListener('wheel', function(event) {
            var xpath = getXPath(event.target);
            window.wheelXPath = xpath;
            window.wheelDeltaY = event.deltaY;
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
                click_xpath = self.driver.execute_script("return window.clickXPath;")
                if click_xpath:
                    self._record_action("click", click_xpath, "")
                    self.driver.execute_script("window.clickXPath = null;")

                # 检查是否有滚轮事件
                wheel_xpath = self.driver.execute_script("return window.wheelXPath;")
                wheel_delta_y = self.driver.execute_script("return window.wheelDeltaY;")
                if wheel_xpath and wheel_delta_y:
                    self._record_action("wheel", wheel_xpath, str(wheel_delta_y))
                    self.driver.execute_script("window.wheelXPath = null; window.wheelDeltaY = null;")

                time.sleep(wait_time)

        except Exception as e:
            # 当浏览器窗口关闭时会抛出异常
            print(f"记录完成: {e}")

        finally:
            if self.driver:
                self.driver.quit()

        return self.actions

    def _record_action(self, action_type, selector, value):
        action = {
            "action": action_type,
            "selector": selector,
            "value": value
        }
        self.actions.append(action)