
async def _session_add(session_maker, item) -> None:
    if not item:
        return

    async with session_maker() as session:
        async with session.begin():
            session.add(item)
            await session.commit()
