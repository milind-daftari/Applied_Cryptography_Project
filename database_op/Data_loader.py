import pandas as pd
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import psycopg2


def string_to_ascii_vector(s):
    return [ord(char) for char in s]

def preprocess_data(data_path, columns=None):
    """
    Preprocesses data from a CSV file, selects specified columns, and returns a DataFrame.

    Args:
        data_path (str): Path to the CSV file containing the data.
        columns (list, optional): List of column names to select for encryption.
            If None, all columns are selected. Defaults to None.

    Returns:
        DataFrame: DataFrame containing the preprocessed data.
    """
    # Read data from CSV using pandas
    data = pd.read_csv(data_path)

    # Select columns if specified
    if columns:
        data = data[columns]

    return data

def encrypt_data(key, plaintext):
    """
    Encrypts plaintext using AES-128 and returns the ciphertext in binary format.

    Args:
        key (bytes): The AES encryption key (16 bytes).
        plaintext (str): The plaintext data to encrypt.

    Returns:
        bytes: The encrypted data in binary format (IV + ciphertext).
    """
    # Generate a random initialization vector (IV)
    iv = os.urandom(16)
    # Create cipher config
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # Encrypt the data
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return (iv + ciphertext)

def main():
    # Encrypt data
    key = os.urandom(16)  # Generate a random AES-128 key
    # Example usage
    data_path = "archive/House_Rent_Dataset.csv"
    columns_to_encrypt = ["BHK", "Rent", "Size", "Bathroom", "Area Locality","Furnishing Status", "City"]  # Optional: Select specific columns

    preprocessed_data = preprocess_data(data_path, columns_to_encrypt)
    # Add a unique ID column
    preprocessed_data['ID'] = range(1, len(preprocessed_data) + 1)
    
    # Calculate the length of each string in the column
    preprocessed_data['length'] = preprocessed_data['City'].apply(len)

    # Find the largest and smallest lengths
    max_length = preprocessed_data['length'].max()
    min_length = preprocessed_data['length'].min()

    print(preprocessed_data)
    print(max_length, min_length)

    # Initialize an empty DataFrame to store encrypted data
    df_encrypted = pd.DataFrame(index=preprocessed_data.index)
    
    # Encrypt each entry in the specified columns
    for column in columns_to_encrypt:
        df_encrypted[column] = preprocessed_data[column].apply(lambda x: encrypt_data(key, str(x)))
    
    # Print outputs to verify
    print(preprocessed_data)
    print(df_encrypted)

    # Connect to the PostgreSQL database
    connection = psycopg2.connect(
        host='localhost',
        database='test_db',
        user='postgres',
        password='admin'
    )
    cursor = connection.cursor()

    # Insert encrypted data into the database
    for index, row in df_encrypted.iterrows():
        cursor.execute(
            "INSERT INTO encrypted_data (encrypted_column1, encrypted_column2, encrypted_column3, encrypted_column4) VALUES (%s, %s, %s, %s)",
            (psycopg2.Binary(row['BHK']), psycopg2.Binary(row['Rent']), psycopg2.Binary(row['Size']), psycopg2.Binary(row['Bathroom']))
        )
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

if __name__ == '__main__':
    main()
