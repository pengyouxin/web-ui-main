import json
import os
from typing import List, Dict, Any, Optional
from browser_controller import BrowserController
from task_manager import TaskManager
from process_recorder import ProcessRecorder


def main():
    # 初始化组件
    process_recorder = ProcessRecorder()
    task_manager = TaskManager()
    browser_controller = BrowserController()

    # 检查是否有已保存的流程
    if task_manager.has_saved_processes():
        print("已存在学习过的流程。")

    try:
        while True:
            print("\n请选择操作：")
            print("1. 进入学习模式")
            print("2. 执行任务")
            print("3. 查看已保存的流程")
            print("4. 退出")

            choice = input("请输入选项 (1-4): ")

            if choice == "1":
                # 学习模式
                process_name = input("请输入此流程的名称（例如：登录邮箱）: ")
                print(f"开始学习流程：{process_name}")
                print("请在浏览器中完成所需操作，系统将记录您的行为...")

                actions = process_recorder.start_recording()

                # 保存流程
                task_manager.save_process(process_name, actions)
                print(f"流程 '{process_name}' 已保存成功！")

            elif choice == "2":
                # 执行任务
                task = input("请描述您的任务（例如：登录邮箱）: ")
                matching_process = task_manager.find_matching_process(task)

                if matching_process:
                    process_name, actions = matching_process
                    print(f"找到匹配的流程：{process_name}，正在执行...")
                    browser_controller.perform_actions(actions)
                    print(f"任务 '{task}' 已完成！")
                else:
                    print("未找到匹配的流程，您可以进入学习模式创建新流程。")

            elif choice == "3":
                # 查看已保存的流程
                processes = task_manager.get_saved_processes()
                if processes:
                    print("已保存的流程：")
                    for i, (name, _) in enumerate(processes, 1):
                        print(f"{i}. {name}")
                else:
                    print("没有已保存的流程。")

            elif choice == "4":
                print("退出程序。")
                break

            else:
                print("无效的选择，请重新输入。")
    except KeyboardInterrupt:
        print("程序被手动中断。")
    finally:
        input("按回车键关闭浏览器并退出程序...")
        browser_controller.close()


if __name__ == "__main__":
    main()