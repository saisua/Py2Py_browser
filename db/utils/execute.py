from sqlalchemy.ext.asyncio import AsyncSession


async def _session_execute(
    session_maker,
    query,
    *,
    commit=False,
    fetch=False,
    scalar=False,
    expunge=False,
    many=False,
):
    async with session_maker() as session:
        session: AsyncSession
        async with session.begin():
            result = await session.execute(query)
            if fetch:
                if many:
                    result = result.fetchall()
                else:
                    result = result.fetchone()
            if scalar:
                if many:
                    result = result.scalars()
                else:
                    result = result.scalar()
            if (fetch or scalar) and many:
                result = result.all()
            if commit:
                await session.commit()
            if expunge:
                if many:
                    # for row in result:
                    #     session.expunge(row)
                    session.expunge_all()
                else:
                    session.expunge(result)
            return result
