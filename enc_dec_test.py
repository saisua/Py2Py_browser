from signal_protocol import (
	state,
	storage,
	address,
	session,
	session_cipher
)

from encryption.initialize_encryption import _generate_encryption_keys


bundle_keys = [
	'identity_key_pair',
	'registration_id',
	'signed_pre_key_id',
	'signed_pre_key_pair',
	'pre_key_id',
	'pre_key_pair',
	'timestamp',
	'session_id'
]

bundle1 = dict(
	zip(bundle_keys, _generate_encryption_keys())
)

bundle2 = dict(
	zip(bundle_keys, _generate_encryption_keys())
)


def make_store(bundle):
	store = storage.InMemSignalProtocolStore(
		bundle['identity_key_pair'],
		bundle['registration_id']
	)

	signed_prekey = state.SignedPreKeyRecord(
		bundle['signed_pre_key_id'],
		bundle['timestamp'],
		bundle['signed_pre_key_pair'],
		bundle['identity_key_pair'].private_key()
		.calculate_signature(bundle['signed_pre_key_pair'].public_key().serialize())
	)
	store.save_signed_pre_key(bundle['signed_pre_key_id'], signed_prekey)

	pre_key_record = state.PreKeyRecord(
		bundle['pre_key_id'],
		bundle['pre_key_pair']
	)
	store.save_pre_key(bundle['pre_key_id'], pre_key_record)

	return store


store1 = make_store(bundle1)
store2 = make_store(bundle2)

addr1 = "User1"
addr2 = "User2"

protocol_address1 = address.ProtocolAddress(
	addr1,
	bundle1['registration_id']
)

protocol_address2 = address.ProtocolAddress(
	addr2,
	bundle2['registration_id']
)

pk_bundle1 = state.PreKeyBundle(
	bundle1['registration_id'],
	store1.get_local_registration_id(),
	bundle1['pre_key_id'],
	bundle1['pre_key_pair'].public_key(),
	bundle1['signed_pre_key_id'],
	bundle1['signed_pre_key_pair'].public_key(),
	bundle1['identity_key_pair'].private_key().calculate_signature(
		bundle1['signed_pre_key_pair'].public_key().serialize()
	),
	bundle1['identity_key_pair'].identity_key()
)

pk_bundle2 = state.PreKeyBundle(
	bundle2['registration_id'],
	store2.get_local_registration_id(),
	bundle2['pre_key_id'],
	bundle2['pre_key_pair'].public_key(),
	bundle2['signed_pre_key_id'],
	bundle2['signed_pre_key_pair'].public_key(),
	bundle2['identity_key_pair'].private_key().calculate_signature(
		bundle2['signed_pre_key_pair'].public_key().serialize()
	),
	bundle2['identity_key_pair'].identity_key()
)

session.process_prekey_bundle(
	protocol_address1,
	store1,
	pk_bundle1
)

session.process_prekey_bundle(
	protocol_address2,
	store1,
	pk_bundle2
)

session.process_prekey_bundle(
	protocol_address1,
	store2,
	pk_bundle1
)

session.process_prekey_bundle(
	protocol_address2,
	store2,
	pk_bundle2
)

test_msg = b"Hello, world!"
ciphertext = session_cipher.message_encrypt(
	store1,
	protocol_address2,
	test_msg
)

print(ciphertext)

msg = session_cipher.message_decrypt(
	store2,
	protocol_address1,
	ciphertext
)

print(msg)
