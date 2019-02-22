from math import ceil

from base64 import b64decode,b64encode
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

from certificados.models import Certificado


def extraer_modulo_y_exponente(public_key):
	"""
	Extrae modulo y exponente de la clave publica que se 
	encuentra en el certificado cargado por el usuario
	"""

	pubkey = RSA.importKey(public_key)

	modulus = pubkey.n
	exponent = pubkey.e


	compacted_modulus = modulus.to_bytes(ceil(modulus.bit_length()/8),'big')
	compacted_exponent = exponent.to_bytes(ceil(exponent.bit_length()/8),'big')

	# print(compacted_modulus)

	b64_modulus = b64encode(compacted_modulus)
	b64_exponent = b64encode(compacted_exponent)

	return (b64_modulus, b64_exponent)


def generar_firma_con_certificado(compania, digest_string):

	certificado = Certificado.objects.get(empresa=compania)

	RSAprivatekey = RSA.importKey(certificado.private_key)
	private_signer = PKCS1_v1_5.new(RSAprivatekey)

	digest = SHA.new()
	digest.update(digest_string.encode('iso8859-1'))
	sign = private_signer.sign(digest)

	modulo, exponente = extraer_modulo_y_exponente(certificado.public_key)

	firma_electronica = {

		'firma': b64encode(sign).decode(),
		'digest': b64encode(digest.hexdigest().encode()).decode(),
		'certificado': certificado.certificado,
		'modulo': modulo.decode(),
		'exponente': exponente.decode()
	}

	return firma_electronica