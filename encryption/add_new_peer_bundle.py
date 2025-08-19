from datetime import datetime
import logging

import bson

# from sqlalchemy import delete

from config import logger, PEERTYPE_CLIENT, PEERTYPE_MYSELF

# from encryption.add_bundle_to_store import add_bundle_to_store
from encryption.utils.decrypt_with_password import decrypt_with_password

from db.models.peers import Peers

from db.utils.add import _session_add
# from db.utils.execute import _session_execute


async def add_new_peer_bundle(
	session_maker,
	peer_bundle: bytes,
	*,
	own_password: str,
	other_password: str,
	add_peer: bool = True,
) -> Peers:
	if logger.isEnabledFor(logging.DEBUG):
		logger.debug("Adding new peer bundle")

	now = datetime.now()

	own_decrypted_bundle = decrypt_with_password(
		peer_bundle,
		own_password,
	)
	decrypted_bundle = decrypt_with_password(
		own_decrypted_bundle,
		other_password,
	)
	deserialized_bundle = bson.loads(decrypted_bundle)

	# print("#### deserialized_bundle", deserialized_bundle)

	# try:
	# 	await _session_execute(
	# 		session_maker,
	# 		delete(Peers).where(
	# 			Peers.address == deserialized_bundle['address']
	# 		),
	# 		commit=True,
	# 	)
	# except Exception as e:
	# 	logging.error("##### Error deleting peer")
	# 	logging.exception(e)

	peer_type = deserialized_bundle.pop('type', None)
	if peer_type == PEERTYPE_MYSELF:
		peer_type = PEERTYPE_CLIENT
	elif peer_type is None:
		raise ValueError("Peer type is required")

	try:
		new_peer = Peers(
			**deserialized_bundle,
			type=peer_type,
			checked_time=now,
		)

		if add_peer:
			await _session_add(session_maker, new_peer)

		return new_peer
	except Exception as e:
		logging.error("Error adding peer")
		logging.exception(e)
		raise

	# add_bundle_to_store(store, deserialized_bundle)
