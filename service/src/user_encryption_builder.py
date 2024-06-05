
from cryptography.hazmat.primitives.serialization import PrivateFormat, BestAvailableEncryption, pkcs12
from cryptography.hazmat.primitives import hashes


class UserInputParser():
    def __init__(self, password, user_input) -> None:
        self.password = password
        self.user_input = user_input
        if self.user_input == "" or len(self.user_input) > 150:
            raise Exception("Encryption Algorithm empty or too long")
        self.builder = PrivateFormat.PKCS12.encryption_builder()

    def run(self):
        while (self.user_input != ""):
            if (self.user_input.startswith('.hmac_hash(')):
                self.handle_hmac_hash()
                continue
            if (self.user_input.startswith('.kdf_rounds(')):
                self.handle_kdf_rounds()
                continue
            if (self.user_input.startswith('.key_cert_algorithm(')):
                self.handle_key_cert_algorithm()
                continue
            else:
                raise Exception("Invalid Syntax")

        return self.builder.build(str.encode(self.password))

    def handle_hmac_hash(self):
        next_bracket = self.user_input.index(')')
        input = self.user_input[11:next_bracket - 1]
        if input.startswith('hashes.'):
            input = input[7:]
        else:
            raise Exception("Invalid Syntax")

        hash_alg = [
            'MD5',
            'SHA1',
            'SHA224',
            'SHA256',
            'SHA384',
            'SHA3_224',
            'SHA3_256',
            'SHA3_384',
            'SHA3_512',
            'SHA512',
            'SHA512_224',
            'SHA512_256',
            'SHAKE128',
            'SHAKE256',
            'SM3']
        if input in hash_alg:
            self.builder = self.builder.hmac_hash(getattr(hashes, input)())
        else:
            raise Exception("Invalid Hashing Algorithm")

        self.user_input = self.user_input[next_bracket + 2:]

    def handle_kdf_rounds(self):
        next_bracket = self.user_input.index(')')
        input = self.user_input[12:next_bracket]
        number = input[:next_bracket]
        try:
            number = int(number)
        except:
            raise Exception("Invalid kdf rounds")

        self.builder = self.builder.kdf_rounds(number)
        self.user_input = self.user_input[next_bracket + 1:]

    def handle_key_cert_algorithm(self):
        next_bracket = self.user_input.index(')')
        input = self.user_input[20:next_bracket]
        if input == 'pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC':
            self.builder = self.builder.key_cert_algorithm(
                pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)

        elif input == 'pkcs12.PBES.PBESv2SHA256AndAES256CBC':
            self.builder = self.builder.key_cert_algorithm(
                pkcs12.PBES.PBESv2SHA256AndAES256CBC)

        else:
            raise Exception("Invalid certification Algorithm")
        self.user_input = self.user_input[next_bracket + 1:]


def main():
    password = "password"
    input = ".kdf_rounds(50000).key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).hmac_hash(hashes.SHA256())"
    try:
        return UserInputParser(password, input).run()
    except:
        return BestAvailableEncryption(str.encode(password))


if __name__ == "__main__":
    main()
