import json
from typing import Dict, List, Any


class TaskManager:
    def __init__(self, processes_file="processes.json"):
        self.processes_file = processes_file
        self.processes = self._load_processes()

    def _load_processes(self) -> Dict[str, List[Dict[str, Any]]]:
        """从文件加载已保存的流程"""
        try:
            with open(self.processes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"加载流程文件出错: {e}")
            return {}

    def save_process(self, name: str, actions: List[Dict[str, Any]]):
        """保存流程到文件"""
        self.processes[name] = actions
        try:
            with open(self.processes_file, "w", encoding="utf-8") as f:
                json.dump(self.processes, f, ensure_ascii=False, indent=4)
            print(f"流程 '{name}' 已保存")
        except Exception as e:
            print(f"保存流程出错: {e}")

    def find_matching_process(self, task: str) -> List[Dict[str, Any]]:
        """查找与任务描述匹配的流程"""
        # 简单的匹配逻辑，实际应用中可以使用更复杂的算法
        best_match = None
        highest_score = 0

        for name, actions in self.processes.items():
            # 计算任务描述与流程名称的相似度
            score = self._calculate_similarity(task, name)
            if score > highest_score:
                highest_score = score
                best_match = actions

        if highest_score > 0.5:  # 设置匹配阈值
            print(f"找到匹配的流程: {list(self.processes.keys())[list(self.processes.values()).index(best_match)]}")
            return best_match
        else:
            print("未找到匹配的流程")
            return []

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（简化版）"""
        # 这里使用简单的Jaccard相似度
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0

        return intersection / union