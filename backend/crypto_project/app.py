from flask import Flask, jsonify, request
from flask_cors import CORS
from openfhe import *
import numpy as np
import os
import pandas as pd
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

# Define global variables
global cryptoContext, keypair, datafolder, serType

Testing = True

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

    return

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

###PKV Code
def remove_all_files(directory):
    """ Removes all files from a directory. """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def convert_rent_to_int(data):
    """ Converts rent values in a pandas dataframe to integers. """
    data['Rent'] = data['Rent'].astype(int)
    return data


def preprocess_data(data_path, columns=None):
    data = pd.read_csv(data_path)
    if columns:
        data = data[columns]
    q1 = data['Rent'].quantile(0.10)
    q3 = data['Rent'].quantile(0.90)
    data = data[(data['Rent'] >= q1) & (data['Rent'] <= q3)]
    data['Rent'] = (data['Rent'] / 1000).astype(int)
    return data

def encrypt_data(plaintext):
    global cryptoContext, keypair
    plaintext_vector = cryptoContext.MakePackedPlaintext(plaintext)
    return cryptoContext.Encrypt(keypair.publicKey, plaintext_vector)

def upload_data_to_db(preprocessed_data):
    global cryptoContext, keypair, serType 
    
    encrypted_files_directory = "Temp_encrypt"
    if not os.path.exists(encrypted_files_directory):
        os.makedirs(encrypted_files_directory)
    remove_all_files(encrypted_files_directory)
    encrypted_rent_files = []
    print("Encrypting")
    
    for i, row in preprocessed_data.iterrows():
        encrypted_rent = encrypt_data([row['Rent']])
        file_path = os.path.join(encrypted_files_directory, f"Rent_encrypted_{i}.bin")
        if not SerializeToFile(file_path, encrypted_rent, serType):
            raise Exception(f"Error writing encrypted data to {file_path}")
        encrypted_rent_files.append(file_path)

    print("Uploading to DB")
    conn = psycopg2.connect(
        dbname="test_db", user="test", password="test", host="db", port="5432"
    )
    cur = conn.cursor()

    # Delete existing data (optional, modify if needed)
    cur.execute("DELETE FROM encrypted_data")

    for i, file_path in enumerate(encrypted_rent_files):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            encrypted_bytes = psycopg2.Binary(file_data)
            city = str(preprocessed_data.iloc[i]['City'])
            bhk = str(preprocessed_data.iloc[i]['BHK'])
            f_status = str(preprocessed_data.iloc[i]['Furnishing Status'])
            broom = str(preprocessed_data.iloc[i]['Bathroom'])
            cur.execute("INSERT INTO encrypted_data (rent, city, furnished_status, bhk, bathroom) VALUES (%s, %s, %s, %s, %s)", (encrypted_bytes, city, f_status, bhk, broom))
    conn.commit()
    cur.close()
    conn.close()
    remove_all_files(encrypted_files_directory)
    print("Done Upload to DB")

def retrieve_and_save_data(city, bhk, f_status, broom):
    # Assuming a directory for this purpose
    retrieve_file_path = "Temp_decrypt"
    if not os.path.exists(retrieve_file_path):
        os.makedirs(retrieve_file_path)
    remove_all_files(retrieve_file_path)
    try:
        conn = psycopg2.connect(
            dbname="test_db",
            user="test",
            password="test",
            host="db",
            port="5432"
        )
        cur = conn.cursor()

        cur.execute("SELECT rent FROM encrypted_data WHERE city = %s AND bhk = %s AND furnished_status = %s AND bathroom = %s", (city, bhk, f_status, broom))
        rows = cur.fetchall()

        if not rows:
            print("No data found for the city:", city)
            return False

        if not os.path.exists(retrieve_file_path):
            os.makedirs(retrieve_file_path)

        for index, row in enumerate(rows):
            file_path = os.path.join(retrieve_file_path, f"rent_data_{city}_{bhk}_{index}.bin")
            with open(file_path, 'wb') as f:
                if row[0]:
                    f.write(row[0].tobytes())
            # print(f"Data for row {index} successfully written to {file_path}")

    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        return True


def compute_homomorphic_average(directory_path="Temp_decrypt"):
    global cryptoContext, serType
    total = None
    count = 0  # To keep track of how many files are processed

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".bin"):
            file_path = os.path.join(directory_path, file_name)
            # Deserialize ciphertext directly from file and add it to the total
            ciphertext, res = DeserializeCiphertext(file_path, serType)
            if not res:
                raise Exception(f"Failed to deserialize ciphertext from {file_path}")
            
            if total is None:
                total = ciphertext  # Initialize total with the first ciphertext
            else:
                cryptoContext.EvalAddInPlace(total, ciphertext)  # Accumulate sum

            count += 1  # Increment count for each processed ciphertext

    if not total:
        raise ValueError("No ciphertexts were loaded, cannot compute average.")

    return total, count

def decrypt_homomorphic_average(ciphertext, count):
    global cryptoContext, keypair
    plaintext = cryptoContext.Decrypt(keypair.secretKey, ciphertext)
    plaintext = str(plaintext).split(' ')[1]
    average = int(plaintext)/ count
    return average

###PKV code end

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

    # Assuming a directory for this purpose
    res = retrieve_and_save_data(str(city), str(bhk), str(furnishing_status), str(bathroom))
    print("Retrieved Data")
    if not res:
        print("No Data Exists for the combination")
    # Compute the homomorphic average
    homomorphic_sum, count = compute_homomorphic_average()
    # Decrypt homomorphic average
    decrypted_homomorphic_average = decrypt_homomorphic_average(homomorphic_sum, count)
    print("Decrypted Homomorphic Average:", decrypted_homomorphic_average * 1000)

    result = int(decrypted_homomorphic_average * 1000)

    if bhk is not None:
        return jsonify(averageRent=result)
    else:
        return jsonify(message="Invalid input"), 400

if __name__ == '__main__':
    setup()
    
    print("Done Key Setup")

    ###PKV
    data_path = "House_Rent_Dataset.csv"
    columns_select = ["Rent", "City", "BHK", "Furnishing Status", "Bathroom"]
    preprocessed_data = preprocess_data(data_path, columns_select)
    print("Done Preporcessing")
    
    

    upload_data_to_db(preprocessed_data)

    print("Encrypted data and uploaded the data to DB")

    if Testing:
        # Assuming a directory for this purpose
        res = retrieve_and_save_data("Kolkata", "2", "Furnished", "1")
        print("Retrieved Data")
        if not res:
            print("No Data Exists for the combination")
        # Compute the homomorphic average
        homomorphic_sum, count = compute_homomorphic_average()
        # Decrypt homomorphic average
        decrypted_homomorphic_average = decrypt_homomorphic_average(homomorphic_sum, count)
        print("Decrypted Homomorphic Average:", decrypted_homomorphic_average * 1000)
                        
        # Group the DataFrame by 'city' and 'BHK' and calculate the average rent
        average_rent = preprocessed_data.groupby(["City", "BHK", "Furnishing Status", "Bathroom"])['Rent'].mean()

        # Access the average rent directly (assuming a single value is returned)
        average_rent_specific = average_rent.loc[("Kolkata", 2, "Furnished", 1)]
        # Print the result without using 'values'
        print(f"Average rent for city '{city}' and BHK {bhk}:", average_rent_specific)

    ###PKV

    app.run(host='0.0.0.0', debug=True)
