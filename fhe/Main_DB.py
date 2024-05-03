import os
import pandas as pd
from openfhe import *
import psycopg2

serType = BINARY
Testing = True

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


def setup_crypto_context():
    parameters = CCParamsBFVRNS()
    parameters.SetPlaintextModulus(65537)
    parameters.SetMultiplicativeDepth(2)
    crypto_context = GenCryptoContext(parameters)
    crypto_context.Enable(PKESchemeFeature.PKE)
    crypto_context.Enable(PKESchemeFeature.KEYSWITCH)
    crypto_context.Enable(PKESchemeFeature.LEVELEDSHE)
    return crypto_context


def encrypt_data(crypto_context, public_key, plaintext):
    plaintext_vector = crypto_context.MakePackedPlaintext(plaintext)
    return crypto_context.Encrypt(public_key, plaintext_vector)


def upload_data_to_db(crypto_context, public_key, preprocessed_data):
    encrypted_files_directory = "Temp_encrypt"
    if not os.path.exists(encrypted_files_directory):
        os.makedirs(encrypted_files_directory)
    remove_all_files(encrypted_files_directory)
    encrypted_rent_files = []
    print("Encrypting")
    for i, row in preprocessed_data.iterrows():
        encrypted_rent = encrypt_data(crypto_context, public_key, [row['Rent']])
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
            cur.execute("INSERT INTO encrypted_data (rent, city, furnished_status, bhk) VALUES (%s, %s, %s, %s)", (encrypted_bytes, city, f_status, bhk))
    conn.commit()
    cur.close()
    conn.close()
    remove_all_files(encrypted_files_directory)
    print("Done Upload to DB")


def retrieve_and_save_data(city, bhk):
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

        cur.execute("SELECT rent FROM encrypted_data WHERE city = %s AND bhk = %s", (city, bhk,))
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


def compute_homomorphic_average(crypto_context, directory_path="Temp_decrypt"):
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
                crypto_context.EvalAddInPlace(total, ciphertext)  # Accumulate sum

            count += 1  # Increment count for each processed ciphertext

    if not total:
        raise ValueError("No ciphertexts were loaded, cannot compute average.")

    return total, count

def decrypt_homomorphic_average(crypto_context, private_key, ciphertext, count):
    plaintext = crypto_context.Decrypt(private_key, ciphertext)
    plaintext = str(plaintext).split(' ')[1]
    average = int(plaintext)/ count
    return average

data_path = "House_Rent_Dataset.csv"
columns_select = ["Rent", "City", "BHK", "Furnishing Status"]
preprocessed_data = preprocess_data(data_path, columns_select)
print("Done Preporcessing")
crypto_context = setup_crypto_context()
keypair = crypto_context.KeyGen()
print("Done Key Setup")
    
upload_data_to_db(crypto_context, keypair.publicKey, preprocessed_data)

print("Encrypted data and uploaded the data to DB")

if Testing:
    # Assuming a directory for this purpose
    res = retrieve_and_save_data("Kolkata", "2")
    print("Retrieved Data")
    if not res:
        print("No Data Exists for the combination")
    # Compute the homomorphic average
    homomorphic_sum, count = compute_homomorphic_average(crypto_context)
    # Decrypt homomorphic average
    decrypted_homomorphic_average = decrypt_homomorphic_average(crypto_context, keypair.secretKey, homomorphic_sum, count)
    print("Decrypted Homomorphic Average:", decrypted_homomorphic_average * 1000)
                    
    # Group the DataFrame by 'city' and 'BHK' and calculate the average rent
    average_rent = preprocessed_data.groupby(['City', 'BHK'])['Rent'].mean()

    # Access the average rent directly (assuming a single value is returned)
    average_rent_specific = average_rent.loc[("Kolkata", 2)]


# User Input Loop
while True:
    city = input("Enter city (or 'q' to quit): ")
    if city.lower() == 'q':
        break
    else:
        bhk = input("Enter bhk (or 'q' to quit): ")
        if city.lower() == 'q':
            break
        else:
            res = retrieve_and_save_data(city, bhk)
            if not res:
                print("No Data Exists for the combination")
                continue
            # Compute the homomorphic average
            homomorphic_sum, count = compute_homomorphic_average(crypto_context)
            # Decrypt homomorphic average
            decrypted_homomorphic_average = decrypt_homomorphic_average(crypto_context, keypair.secretKey, homomorphic_sum, count)
            print("Decrypted Homomorphic Average:", decrypted_homomorphic_average * 1000)
                
            # Group the DataFrame by 'city' and 'BHK' and calculate the average rent
            average_rent = preprocessed_data.groupby(['City', 'BHK'])['Rent'].mean()

            # Access the average rent directly (assuming a single value is returned)
            average_rent_specific = average_rent.loc[(city, int(bhk))]

            # Print the result without using 'values'
            print(f"Average rent for city '{city}' and BHK {bhk}:", average_rent_specific)