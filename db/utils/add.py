from typing import Callable, Any
import logging
import traceback

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


async def _session_add(
	session_maker: (
		Callable[[], AsyncSession] | AsyncSession | AsyncSessionTransaction
	),
	item: Any,
) -> None:
	if not item:
		return

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
		session.add(item)
	except Exception as e:
		logging.error("Error executing add query for item: %s", item)
		logging.error("Call stack:\n%s", "".join(traceback.format_stack()))
		logging.exception(e)
		await session.rollback()
		raise
	finally:
		if close_transaction:
			await session.flush()
			await session.commit()
			await transaction.__aexit__(None, None, None)

		if close_session:
			await asession.__aexit__(None, None, None)
