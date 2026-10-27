"""交通规范 Agent 的 Gradio 网页界面（流式回答 + 工具日志 + 来源展示）"""
import gradio as gr
from agent.agent import run_agent_stream


def chat(message, history):
    """流式版：把 Agent 吐出的事件拼成界面文本"""
    text = ""
    for type_, content in run_agent_stream(message):
        if type_ == "answer":
            text += content
            yield text
        elif type_ == "log":
            text += f"\n> 🔧 {content}\n\n"
            yield text
        elif type_ == "sources":
            if content:
                text += "\n\n**📚 引用来源：**\n" + "\n".join(f"- {s}" for s in content)
            yield text



EXAMPLES = [
    "公路分为哪几个技术等级？",
    "城市道路和公路对“设计速度”的规定有什么不同？",
    "规范要求高速公路的净高是多少？换算成厘米呢？",
]

demo = gr.ChatInterface(fn=chat, title="交通规范智能问答", examples=EXAMPLES)

if __name__ =="__main__":
    demo.launch()
