import asyncio


async def remove_tasks_forever(tasks: list, delay: float = 10):
    while True:
        await asyncio.sleep(delay)
        for task in tasks:
            if task.cancelled() or task.done():
                tasks.remove(task)
