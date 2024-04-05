# 使用AioDownloader在windows系统下挂代理会产生问题
import asyncio
import platform
system = platform.system().lower()
if system == "windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )