"""Agent 核心：工具注册 + ReAct 主循环"""
import os
import json
import logging
import re

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

# 工具 schema：模型据此决定调哪个工具、传什么参数
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
    """ReAct 主循环：模型决定调工具 → 执行 → 结果回填 → 直到它不再调工具"""
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
            return msg.content



def run_agent_stream(question):
    """流式版（生成器）：yield (类型, 内容)

    类型：
      "log"     → 工具调用日志，给界面展示
      "answer"  → 回答正文片段
      "sources" → 本次引用的来源，最后 yield 一次
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    sources = []          # 收集本次引用的来源，去重保序
    step = 0

    while True:
        step += 1
        stream = llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            temperature=0,
            stream=True,
        )

        content_parts = []   # 本轮的文字输出
        tool_buf = {}        # index -> {id, name, arguments}；流式下工具调用是分片到达的

        for chunk in stream:
            delta = chunk.choices[0].delta

            if delta.content:
                content_parts.append(delta.content)
                yield ("answer", delta.content)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_buf:
                        tool_buf[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_buf[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_buf[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_buf[idx]["arguments"] += tc.function.arguments

        if tool_buf:
            # 存回历史：文字和 tool_calls 必须成对出现，否则下一轮请求直接 400
            messages.append({
                "role": "assistant",
                "content": "".join(content_parts) or None,
                "tool_calls": [
                    {
                        "id": t["id"],
                        "type": "function",
                        "function": {"name": t["name"], "arguments": t["arguments"]},
                    }
                    for t in tool_buf.values()
                ],
            })

            # 执行工具并回填结果，tool_call_id 必须与请求里的一致
            for t in tool_buf.values():
                name = t["name"]
                args = json.loads(t["arguments"])

                if name == "search_rules":
                    yield ("log", f"检索：{args.get('query')}")
                    result = search_rules(args["query"])
                elif name == "compare_rules":
                    yield ("log", f"对比：{args.get('topic')}")
                    result = compare_rules(args["topic"])
                elif name == "convert_unit":
                    yield ("log", f"换算：{args.get('value')} {args.get('from_unit')} → {args.get('to_unit')}")
                    result = convert_unit(args["value"], args["from_unit"], args["to_unit"])
                else:
                    result = f"未知工具：{name}"

                # 两个工具的输出格式不同，各抓一遍来源
                found = re.findall(r"【来源：(.+?)】", result)
                found += re.findall(r"===== (.+?) 的相关条文 =====", result)
                for s in found:
                    if s not in sources:
                        sources.append(s)

                messages.append({"role": "tool", "tool_call_id": t["id"], "content": result})

            if step >= MAX_STEPS:
                yield ("log", "（达到步数上限，停止）")
                break
        else:
            # 没有工具调用 = 这一轮就是最终回答，而且已经流完了
            break

    yield ("sources", sources)
