import json
import os
from typing import List, Dict, Any, Optional, Tuple
from difflib import get_close_matches


class TaskManager:
    def __init__(self, processes_file: str = "processes.json"):
        self.processes_file = processes_file
        self.processes = self._load_processes()

    def _load_processes(self) -> Dict[str, List[Dict[str, Any]]]:
        """从文件加载已保存的流程"""
        if os.path.exists(self.processes_file):
            try:
                with open(self.processes_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载流程文件时出错: {e}")
        return {}

    def save_process(self, process_name: str, actions: List[Dict[str, Any]]):
        """保存新的流程"""
        self.processes[process_name] = actions
        self._save_processes()

    def _save_processes(self):
        """将流程保存到文件"""
        with open(self.processes_file, "w", encoding="utf-8") as f:
            json.dump(self.processes, f, ensure_ascii=False, indent=2)

    def find_matching_process(self, task_description: str) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
        """查找与任务描述匹配的流程"""
        if not self.processes:
            return None

        # 使用difflib获取最接近的匹配
        process_names = list(self.processes.keys())
        matches = get_close_matches(task_description, process_names, n=1, cutoff=0.3)

        if matches:
            best_match = matches[0]
            return best_match, self.processes[best_match]

        return None

    def get_saved_processes(self) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """获取所有已保存的流程"""
        return list(self.processes.items())

    def has_saved_processes(self) -> bool:
        """检查是否有已保存的流程"""
        return bool(self.processes)