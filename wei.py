import argparse
import asyncio
import os
import json
from src.webui.webui_manager import WebuiManager
from src.agent.browser_use.browser_use_agent import BrowserUseAgent
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import CustomBrowserContext
from src.utils import llm_provider
from src.utils.config import model_names
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContextConfig
import tempfile
import sys
from process_recorder import ProcessRecorder
from task_manager import TaskManager
from browser_controller import BrowserController

# 定义一个较大的窗口尺寸，近似最大化
MAXIMIZED_WIDTH = 3840  # 超宽屏常见宽度
MAXIMIZED_HEIGHT = 2160  # 常见的 4K 高度

# 读取配置文件
def read_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("未找到配置文件 config.json，请确保该文件存在于当前目录下。")
        sys.exit(1)


def setup_agent(webui_manager, task, config):
    # 初始化浏览器使用代理
    webui_manager.init_browser_use_agent()

    # 获取配置文件中的浏览器路径和用户数据目录
    browser_binary_path = config.get("BROWSER_PATH", None)
    browser_user_data = config.get("BROWSER_USER_DATA", None)
    extra_browser_args = []
    if browser_user_data:
        extra_browser_args += [f"--user-data-dir={browser_user_data}"]

    # 设置窗口尺寸为近似最大化
    extra_browser_args += [f"--window-size={MAXIMIZED_WIDTH},{MAXIMIZED_HEIGHT}"]

    # 创建自定义浏览器和上下文
    browser = CustomBrowser(
        config=BrowserConfig(
            headless=False,
            browser_binary_path=browser_binary_path,
            extra_browser_args=extra_browser_args,
            new_context_config=BrowserContextConfig(
                window_width=MAXIMIZED_WIDTH,
                window_height=MAXIMIZED_HEIGHT,
            )
        )
    )
    context = CustomBrowserContext(browser=browser)

    # 初始化LLM
    provider = "deepseek"  # 可以根据需要修改
    model_name = "deepseek-chat"  # 可以根据需要修改
    temperature = 0.6  # 可以根据需要修改
    base_url = config.get("DEEPSEEK_ENDPOINT")
    api_key = config.get("DEEPSEEK_API_KEY")
    if api_key is None:
        print("配置文件中未找到 DEEPSEEK_API_KEY，请检查 config.json 文件。")
        sys.exit(1)

    llm = llm_provider.get_llm_model(
        provider=provider,
        model_name=model_name,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key
    )

    # 创建浏览器使用代理
    agent = BrowserUseAgent(
        task=task,
        llm=llm,
        browser=browser,
        browser_context=context
    )
    webui_manager.bu_agent = agent
    return agent


async def run_agent(agent):
    # 运行代理
    history = await agent.run()
    return history


def main():
    webui_manager = WebuiManager()
    # 读取配置文件
    config = read_config()
    process_recorder = ProcessRecorder()
    task_manager = TaskManager()
    browser_controller = BrowserController()

    while True:
        # 询问是否进入学习模式
        choice = input("是否进入学习模式？(y/n/quit): ")
        if choice.lower() == 'quit':
            print("退出程序。")
            break
        elif choice.lower() == 'y':
            process_name = input("请输入此流程的名称（例如：登录邮箱）: ")
            print(f"开始学习流程：{process_name}")
            print("请在浏览器中完成所需操作，系统将记录您的行为...")

            # 推迟浏览器的启动到 start_recording 方法内部
            actions = process_recorder.start_recording()

            # 保存流程
            task_manager.save_process(process_name, actions)
            print(f"流程 '{process_name}' 已保存成功！")
        elif choice.lower() == 'n':
            # 提示用户输入任务
            task = input("用户指令：")
            if not task:
                print("请输入有效的任务。")
                continue

            # 检查是否有匹配的流程
            matching_process = task_manager.find_matching_process(task)
            if matching_process:
                choice = input(f"是否匹配流程？(y/n): ")
                if choice.lower() == 'y':
                    print(f"找到匹配的流程，正在执行...")
                    # 推迟浏览器的启动到 perform_actions 方法内部
                    browser_controller.perform_actions(matching_process)
                    print(f"任务 '{task}' 已完成！")
                else:
                    agent = setup_agent(webui_manager, task, config)
                    # 使用 asyncio.run() 来运行异步函数
                    history = asyncio.run(run_agent(agent))
                    print("Agent history:", history)
            else:
                agent = setup_agent(webui_manager, task, config)
                # 使用 asyncio.run() 来运行异步函数
                history = asyncio.run(run_agent(agent))
                print("Agent history:", history)
        else:
            print("无效的选择，请重新输入。")

    # 关闭浏览器
    browser_controller.close()

    # 防止程序自动关闭，等待用户输入
    input("按回车键退出...")


if __name__ == "__main__":
    main()