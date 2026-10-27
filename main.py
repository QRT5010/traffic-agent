"""命令行入口：依次跑 TEST_QUESTIONS 里的问题（需在项目根目录运行）

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
# openai 3.x 底层走 httpx2，压掉逐条请求的日志
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
