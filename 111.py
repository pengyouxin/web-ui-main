import gradio as gr
import requests

# DeepSeek API 的配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"
DEEPSEEK_API_KEY = "sk-974346a3d84b49f2819e07f67dd9efef"


# 调用 DeepSeek API 的函数
def call_deepseek_api(message, history):
    # 构造请求数据
    data = {
        "model": "deepseek-chat",  # 模型名称
        "messages": [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            [{"role": "user", "content": msg[0]} for msg in history],  # 历史记录格式调整
            {"role": "user", "content": message}
        ]
    }

    # 发送请求
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)

    # 解析响应
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"错误: {response.status_code}, {response.text}"


# Gradio 对话逻辑函数
def chat_with_bot(message, history):
    history = history or []  # 初始化历史记录
    response = call_deepseek_api(message, history)  # 调用 DeepSeek API
    history.append([message, response])  # 追加对话到历史
    return history, history  # 返回更新后的历史


# 自定义 CSS（从之前代码整合，若有调整可自行修改）
custom_css = """
.gradio-container {
    max-width: 800px;
    margin: auto;
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.gradio-markdown h1 {
    font-size: 28px;
    color: #333;
    text-align: center;
    margin-bottom: 20px;
}

.gradio-textbox textarea {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
    padding: 10px;
}

.gradio-button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}

.gradio-button:hover {
    background-color: #0056b3;
}

.gradio-chatbot {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 10px;
    max-height: 400px;
    overflow-y: auto;
}

.gradio-chatbot .user {
    background-color: #007bff;
    color: white;
    border-radius: 10px 10px 0 10px;
    padding: 10px;
    margin: 5px 0;
    max-width: 70%;
    align-self: flex-end;
}

.gradio-chatbot .bot {
    background-color: #f1f1f1;
    color: #333;
    border-radius: 10px 10px 10px 0;
    padding: 10px;
    margin: 5px 0;
    max-width: 70%;
    align-self: flex-start;
}

.gradio-examples {
    background-color: #f1f1f1;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 10px;
    margin-top: 10px;
}

.gradio-examples .example {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 5px 10px;
    margin: 5px 0;
    cursor: pointer;
}

.gradio-examples .example:hover {
    background-color: #f9f9f9;
}
"""

# 创建 Gradio 界面（整合两段截图代码）
with gr.Blocks(css=custom_css) as demo:
    # 标题和描述
    gr.Markdown("# 🤖 DeepSeek 聊天机器人")
    gr.Markdown("欢迎使用 DeepSeek 聊天机器人！你可以在这里与 AI 进行对话。")

    # 聊天窗口
    chatbot = gr.Chatbot(label="聊天记录", bubble_full_width=False)  # 调整聊天窗口样式
    state = gr.State()  # 用于存储聊天历史

    # 输入区域
    with gr.Row():
        user_input = gr.Textbox(
            label="输入消息",
            placeholder="请输入你的问题...",
            lines=2,  # 增加输入框高度
            max_lines=5  # 限制最大高度
        )
        submit_button = gr.Button("发送", variant="primary")  # 补充按钮定义（截图里没写，需补上才能绑定事件）

    # 绑定事件（截图里的逻辑，补充按钮后关联）
    submit_button.click(
        chat_with_bot,
        inputs=[user_input, state],
        outputs=[chatbot, state]
    )

    # 添加示例问题
    gr.Examples(
        examples=["你好！", "你能做什么？", "告诉我一个笑话。"],
        inputs=user_input,
        label="试试这些示例问题："
    )

# 启动 Gradio 应用
if __name__ == "__main__":
    demo.launch()