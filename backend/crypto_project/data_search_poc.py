from openfhe import *
import os

# Define global variables
global cryptoContext, keypair, datafolder, serType


def setup():
    global cryptoContext, keypair, datafolder, serType
    datafolder = 'demoData'
    serType = BINARY  # BINARY or JSON

    # Ensure the data directory exists
    os.makedirs(datafolder, exist_ok=True)
    print(f"Created or verified directory `{datafolder}` for storing data.")

    # Initialize Crypto Context and Key Generation
    parameters = CCParamsBFVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)

    cryptoContext = GenCryptoContext(parameters)
    cryptoContext.Enable(PKESchemeFeature.PKE)
    cryptoContext.Enable(PKESchemeFeature.KEYSWITCH)
    cryptoContext.Enable(PKESchemeFeature.LEVELEDSHE)

    if not SerializeToFile(datafolder + "/cryptocontext.txt", cryptoContext, serType):
        raise Exception(
            "Error writing serialization of the crypto context to cryptocontext.txt")
    print("The cryptocontext has been serialized.")

    keypair = cryptoContext.KeyGen()
    if not keypair:
        raise Exception("Key generation failed.")

    SerializeToFile(datafolder + "/key-public.txt", keypair.publicKey, serType)
    SerializeToFile(datafolder + "/key-private.txt",
                    keypair.secretKey, serType)

    cryptoContext.EvalMultKeyGen(keypair.secretKey)
    cryptoContext.SerializeEvalMultKey(
        datafolder + "/key-eval-mult.txt", serType)
    cryptoContext.EvalRotateKeyGen(keypair.secretKey, [1, 2, -1, -2])
    cryptoContext.SerializeEvalAutomorphismKey(
        datafolder + "/key-eval-rot.txt", serType)

    print("Keys and evaluation keys have been serialized.")
    # Encrypt and store values 1 through 8
    encrypt_and_store(list(range(1, 9)))


def encrypt_and_store(values):
    global cryptoContext, keypair, datafolder, serType
    for idx, value in enumerate(values):
        plaintext = cryptoContext.MakePackedPlaintext([value])
        ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
        filename = f"{datafolder}/ciphertext{idx}.txt"
        SerializeToFile(filename, ciphertext, serType)
        print(f"Ciphertext for {value} stored as {filename}")


def load_encrypted_database():
    filename = f"{datafolder}/db.txt"
    encrypted_values = []
    with open(filename, 'r') as file:
        for line in file:
            path = f"{datafolder}/{line.strip()}"
            ciphertext, success = DeserializeCiphertext(path, serType)
            if success:
                encrypted_values.append(ciphertext)
                print(f"Loaded ciphertext from {path}")
            else:
                print(f"Failed to load ciphertext from {path}")
    return encrypted_values


def encrypt_input(value):
    plaintext = cryptoContext.MakePackedPlaintext([value])
    ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
    print(f"Input {value} encrypted.")
    return ciphertext


def negate_ciphertext(ciphertext):
    negated = cryptoContext.EvalNegate(ciphertext)
    print("Ciphertext negated.")
    return negated


def find_match(negated_ciphertext, database):
    for ct in database:
        result_ct = cryptoContext.EvalAdd(ct, negated_ciphertext)
        result_pt = cryptoContext.Decrypt(keypair.secretKey, result_ct)
        result_str = str(result_pt)  # Convert Plaintext to string if possible
        # Assuming the string conversion gives you the number at the start of the string
        # Adjust index based on actual format
        value = int(result_str.split()[0])
        if value == 0:
            original_pt = cryptoContext.Decrypt(keypair.secretKey, ct)
            original_value = int(str(original_pt).split()[0])
            return original_value
    return "No match found"


def encrypted_search(value):
    encrypted_input = encrypt_input(value)
    negated_input = negate_ciphertext(encrypted_input)
    encrypted_database = load_encrypted_database()
    match = find_match(negated_input, encrypted_database)
    if match != "No match found":
        print("Matching plaintext value:", match)
    else:
        print("No matching entry found.")
    return match
