
async def _session_add_all(session_maker, items) -> None:
    if not items:
        return

    async with session_maker() as session:
        async with session.begin():
            session.add_all(items)
            await session.commit()
