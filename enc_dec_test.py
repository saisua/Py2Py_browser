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
	'sid'
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
	print("Created store")

	signed_prekey = state.SignedPreKeyRecord(
		bundle['signed_pre_key_id'],
		bundle['timestamp'],
		bundle['signed_pre_key_pair'],
		bundle['identity_key_pair'].private_key()
		.calculate_signature(bundle['signed_pre_key_pair'].public_key().serialize())
	)
	store.save_signed_pre_key(bundle['signed_pre_key_id'], signed_prekey)
	print("Saved signed pre key")

	pre_key_record = state.PreKeyRecord(
		bundle['pre_key_id'],
		bundle['pre_key_pair']
	)
	store.save_pre_key(bundle['pre_key_id'], pre_key_record)
	print("Saved pre key")

	return store


store1 = make_store(bundle1)
store2 = make_store(bundle2)

addr1 = "User1"
addr2 = "User2"

protocol_address1 = address.ProtocolAddress(
	addr1,
	bundle1['registration_id']
)
print("Created protocol address 1")

protocol_address2 = address.ProtocolAddress(
	addr2,
	bundle2['registration_id']
)
print("Created protocol address 2")

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
print("Created pre key bundle 1")

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
print("Created pre key bundle 2")

session.process_prekey_bundle(
	protocol_address1,
	store1,
	pk_bundle1
)
print("Processed pre key bundle 1 for store 1")

session.process_prekey_bundle(
	protocol_address2,
	store1,
	pk_bundle2
)
print("Processed pre key bundle 2 for store 1")

session.process_prekey_bundle(
	protocol_address1,
	store2,
	pk_bundle1
)
print("Processed pre key bundle 1 for store 2")

session.process_prekey_bundle(
	protocol_address2,
	store2,
	pk_bundle2
)
print("Processed pre key bundle 2 for store 2")

test_msg = b"Hello, world!"
ciphertext = session_cipher.message_encrypt(
	store1,
	protocol_address2,
	test_msg
)
print("\nEncrypted message:")

print(ciphertext)

msg = session_cipher.message_decrypt(
	store2,
	protocol_address1,
	ciphertext
)
print("\nDecrypted message:")

print(msg)
