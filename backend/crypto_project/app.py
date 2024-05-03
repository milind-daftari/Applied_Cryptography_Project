from flask import Flask, jsonify, request
from flask_cors import CORS
from openfhe import *
import numpy as np
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

# Define global variables
global cryptoContext, keypair, datafolder, serType

def setup():
    global cryptoContext, keypair, datafolder, serType
    datafolder = 'demoData'
    serType = JSON  # BINARY or JSON

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

    encrypt_and_store([1, 2, 3, 4, 5, 6, 7, 8])

def encrypt_and_store(values):
    global cryptoContext, keypair, datafolder, serType
    fn = open(f"{datafolder}/database","wb")
    for idx, value in enumerate(values):
        plaintext = cryptoContext.MakePackedPlaintext([value])
        ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
        filename = f"{datafolder}/ciphertext.txt"
        SerializeToFile(filename, ciphertext, serType)
        with open(f"{datafolder}/ciphertext.txt","rb") as file:
            cipherline = file.read()
            fn.write(cipherline)
            fn.write(b"ENDENDEND")
        file.close()
    fn.close()
    #create_dbtxt(values)

'''def create_dbtxt(values):
    fn = f"{datafolder}/db.txt"
    with open(fn, 'w') as file:
        for idx in values:
            file.write(f"ciphertext{idx}.txt")
            file.write("\n")'''

def encrypt_input(value):
    plaintext = cryptoContext.MakePackedPlaintext([int(value)])
    ciphertext = cryptoContext.Encrypt(keypair.publicKey, plaintext)
    return ciphertext

def negate_ciphertext(ciphertext):
    return cryptoContext.EvalNegate(ciphertext)

def find_match(negated_ciphertext, database):
    for ct in database:
        result_ct = cryptoContext.EvalAdd(ct, negated_ciphertext)
        result_pt = cryptoContext.Decrypt(keypair.secretKey, result_ct)
        value = int(str(result_pt).split()[1])
        if value == 0:
            original_pt = cryptoContext.Decrypt(keypair.secretKey, ct)
            return int(str(original_pt).split()[1])
    return "No match found"

'''def load_encrypted_database(filename):
    encrypted_values = []
    with open(filename, 'r') as file:
        fn = open("ciphertext","wb")
        # Read the entire file content at once
        content = file.read()
        # Split the content based on three consecutive newline characters
        entries = content.split('ENDENDEND')
        print(len(entries))
        for i in range(len(entries)):
            fn.write(entries[i].encode())
            ct, _ = DeserializeCiphertext("ciphertext.txt", serType)
            encrypted_values.append(ct)
    return encrypted_values'''

def encrypted_search(value):
    encrypted_input = encrypt_input(value)
    negated_input = negate_ciphertext(encrypted_input)
    
    encrypted_values = []
    with open(f"{datafolder}/database", 'r') as file:
        content = file.read()
        entries = content.split('ENDENDEND')
        print("Number of entries:", len(entries))
        
        # Ensure the temporary file is opened only once
        with open(f"{datafolder}/temporary.txt", "wb") as fn:
            for entry in entries:
                if entry.strip():  # Check if the entry is not empty
                    # Write each entry to the file and read it back for deserialization
                    fn.seek(0)  # Reset file pointer to the start of the file
                    fn.truncate()  # Clear existing content
                    fn.write(entry.strip().encode())
                    fn.flush()  # Ensure data is written to disk

                    ct, _ = DeserializeCiphertext(f"{datafolder}/temporary.txt", serType)
                    encrypted_values.append(ct)

    print("Encrypted values:", encrypted_values)
    return find_match(negated_input, encrypted_values)


@app.route('/api/filter-options', methods=['GET'])
def filter_options():
    bhk = request.args.get('bhk', type=int)
    city = request.args.get('city')
    furnishing_status = request.args.get('furnishingStatus')
    bathroom = request.args.get('bathroom')
    result = encrypted_search(bhk)
    if bhk is not None:
        return jsonify(averageRent=result)
    else:
        return jsonify(message="Invalid input"), 400

if __name__ == '__main__':
    setup()

    app.run(host='0.0.0.0', debug=True)
