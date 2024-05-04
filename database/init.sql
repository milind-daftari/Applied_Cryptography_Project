-- Set default search_path to new database (This line is not actually needed as it won't do anything outside of session)
-- SET search_path TO test_db;

-- Connect to the new database and create the table
\c test_db

CREATE TABLE encrypted_data (
  id SERIAL PRIMARY KEY,
  rent BYTEA,
  bhk VARCHAR(255),
  city VARCHAR(255),
  furnished_status VARCHAR(255),
  bathroom VARCHAR(255)
);