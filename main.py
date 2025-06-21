import json
from process_recorder import ProcessRecorder
from browser_controller import BrowserController
from task_manager import TaskManager

if __name__ == "__main__":
    process_recorder = ProcessRecorder()
    browser_controller = BrowserController()
    task_manager = TaskManager()

    while True:
        print("\n===== 自动化浏览器操作工具 =====")
        print("1. 学习模式 - 记录操作")
        print("2. 执行模式 - 执行任务")
        print("3. 退出")

        choice = input("请选择功能: ")

        if choice == "1":
            process_name = input("请输入此流程的名称（例如：登录邮箱）: ")
            actions = process_recorder.start_recording()
            task_manager.save_process(process_name, actions)

        elif choice == "2":
            task = input("请描述您的任务（例如：登录邮箱）: ")
            matching_process = task_manager.find_matching_process(task)
            if matching_process:
                browser_controller.perform_actions(matching_process)

        elif choice == "3":
            print("感谢使用，再见！")
            break

        else:
            print("无效的选择，请重新输入")