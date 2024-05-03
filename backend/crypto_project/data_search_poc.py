from openfhe import *
import numpy as np
import os

# Define global variables
global cryptoContext, keypair, datafolder, serType


def setup():
    global cryptoContext, keypair, datafolder, serType
    datafolder = 'demoData'
    serType = BINARY  # BINARY or JSON

    if not os.path.exists(datafolder):
        os.makedirs(datafolder)
        print(f"Created directory `{datafolder}` for storing data.")
    print("This program requires the subdirectory `" + datafolder +
          "' to exist, otherwise you will get an error writing serializations.")

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
    encrypt_and_store([1, 2, 3, 4, 5, 6, 7, 8])

# Encrypt integers and store in the database


def encrypt_and_store(values):
    global cryptoContext, keypair, datafolder, serType
    for idx, value in enumerate(values):
        plaintext = cryptoContext.MakePackedPlaintext([value])
        ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
        filename = f"{datafolder}/ciphertext{idx}.txt"
        SerializeToFile(filename, ciphertext, serType)
        print(f"Ciphertext for {value} stored as {filename}")
    with open(f"{datafolder}/db.txt", "w") as f:
        for idx in range(len(values)):
            f.write(f"ciphertext{idx}.txt\n")

# Load encrypted database


def load_encrypted_database(filename):
    with open(filename, 'r') as file:
        encrypted_values = []
        for line in file:
            path = f"{datafolder}/{line.strip()}"
            ct, success = DeserializeCiphertext(path, serType)
            if success:
                encrypted_values.append(ct)
                print(f"Loaded ciphertext from {path}")
            else:
                print(f"Failed to load ciphertext from {path}")
        return encrypted_values

# Encrypt input and negate ciphertext


def encrypt_input(value):
    plaintext = cryptoContext.MakePackedPlaintext([value])
    ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
    print(f"Input {value} encrypted.")
    return ciphertext


def negate_ciphertext(ciphertext):
    negated = cryptoContext.EvalNegate(ciphertext)
    print("Ciphertext negated.")
    return negated

# Search for the match


def find_match(negated_ciphertext, database):
    for ct in database:
        # Adding the negated ciphertext to each database entry
        result_ct = cryptoContext.EvalAdd(ct, negated_ciphertext)
        result_pt = cryptoContext.Decrypt(keypair.secretKey, result_ct)
        strresult = str(result_pt)
        value = int(strresult.split()[1])
        # print(value)
        # Checking if the result decrypts to zero (indicating a match)
        if value == 0:
            original_pt = cryptoContext.Decrypt(keypair.secretKey, ct)
            original_pt = str(original_pt).split()[1]
            return original_pt  # Returning the original plaintext of the matching ciphertext
    return "No match found"


# Perform the encrypted search
def encrypted_search(value):
    encrypted_input = encrypt_input(value)
    negated_input = negate_ciphertext(encrypted_input)
    encrypted_database = load_encrypted_database(f"{datafolder}/db.txt")
    match = find_match(negated_input, encrypted_database)
    if match is not None:
        print("Matching plaintext value:", match)
    else:
        print("No matching entry found.")

# setup()
# input_value = int(input("Enter an integer to search: "))
# encrypted_search(input_value)
