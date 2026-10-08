"""Agent 核心：工具注册 + ReAct 主循环"""
import os
import json
import logging

from openai import OpenAI
from dotenv import load_dotenv

from config import LLM_MODEL, LLM_BASE_URL, SYSTEM_PROMPT, MAX_STEPS
from tools.search_tools import search_rules, compare_rules
from tools.unit_tools import convert_unit

load_dotenv()
logger = logging.getLogger(__name__)

llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=LLM_BASE_URL,
)

# ---------- 工具说明书（模型据此决定调哪个工具） ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_rules",
            "description": "查询交通规范条文。当用户询问公路或城市道路的规范要求时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要查询的规范问题"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_rules",
            "description": "对比两份规范（城市道路 GB55011 与公路 JTG B01）对同一主题的规定。当用户想对比两种规范的要求时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "要对比的主题，例如：设计速度、净高、车道宽度"},
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_unit",
            "description": "单位换算，支持长度（mm/cm/m/km）和速度（m/s、km/h）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "数值"},
                    "from_unit": {"type": "string", "description": "源单位"},
                    "to_unit": {"type": "string", "description": "目标单位"},
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
]


def run_agent(question):
    """ReAct 主循环：模型决定调工具 → 执行 → 结果回填 → 直到给出最终回答"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    step = 0
    while True:
        step += 1
        response = llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            temperature=0,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                name = tool_call.function.name

                if name == "search_rules":
                    logger.info("检索：%s", args.get("query"))
                    result = search_rules(args["query"])
                elif name == "compare_rules":
                    logger.info("对比：%s", args.get("topic"))
                    result = compare_rules(args["topic"])
                elif name == "convert_unit":
                    logger.info("换算：%s %s → %s", args.get("value"), args.get("from_unit"), args.get("to_unit"))
                    result = convert_unit(args["value"], args["from_unit"], args["to_unit"])
                else:
                    result = f"未知工具：{name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            if step >= MAX_STEPS:
                logger.warning("达到步数上限，停止")
                break
        else:
            print(msg.content)
            break
