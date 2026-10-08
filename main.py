"""程序入口：跑 Agent 的测试问题

用法（必须在项目根目录运行）：
    python main.py
"""
import logging

from config import TEST_QUESTIONS
from agent.agent import run_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
# 屏蔽第三方库的请求流水日志（openai 3.x 底层用的是 httpx2，老 httpx 也一起压上）
logging.getLogger("httpx2").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    for q in TEST_QUESTIONS:
        print("=" * 60)
        print(f"问：{q}")
        print("-" * 60)
        run_agent(q)
        print()


if __name__ == "__main__":
    main()
