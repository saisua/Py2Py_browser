import logging
import traceback
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


async def _session_execute(
	session_maker: (
		Callable[[], AsyncSession]
		| AsyncSession  # noqa: W503
		| AsyncSessionTransaction  # noqa: W503
	),
	query,
	*,
	commit=False,
	fetch=False,
	scalar=False,
	expunge=False,
	many=False,
):
	if not isinstance(session_maker, (AsyncSessionTransaction, AsyncSession)):
		close_session = True
		asession = session_maker()
		session = await asession.__aenter__()
	else:
		close_session = False
		asession = None
		session = session_maker

	if isinstance(session, AsyncSession):
		close_transaction = True
		transaction = await session.begin().__aenter__()
	else:
		close_transaction = False
		transaction = session
		session = transaction.session

	try:
		result = await session.execute(query)
		if fetch:
			if many:
				result = result.fetchall()
			else:
				result = result.fetchone()
		if result is None:
			return
		if scalar:
			if many:
				result = result.scalars()
				result = result.all()
			else:
				result = result.scalar()
		if result is None:
			return
		if commit:
			await session.flush()
			await session.commit()
		if expunge:
			if many:
				# for row in result:
				#     session.expunge(row)
				session.expunge_all()
			else:
				session.expunge(result)
		return result
	except Exception as e:
		logging.error("Error executing execute query: %s", query)
		logging.error("Call stack:\n%s", "".join(traceback.format_stack()))
		logging.exception(e)
		await session.rollback()
		raise
	finally:
		if close_transaction:
			await transaction.__aexit__(None, None, None)

		if close_session:
			await asession.__aexit__(None, None, None)
