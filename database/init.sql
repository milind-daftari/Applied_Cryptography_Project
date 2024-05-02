-- Set default search_path to new database (This line is not actually needed as it won't do anything outside of session)
-- SET search_path TO test_db;

-- Connect to the new database and create the table
\c test_db

CREATE TABLE encrypted_data (
  id SERIAL PRIMARY KEY,
  data1 BYTEA,
  data2 BYTEA,
  data3 BYTEA,
  data4 BYTEA,
  data5 BYTEA
);

-- Insert test data
INSERT INTO encrypted_data (data1, data2, data3, data4, data5) VALUES
  ('\x54686973', '\x69732073', '\x6f6d6520', '\x62797465', '\x64617461'),
  ('\x12345678', '\x6f746865', '\x72206279', '\x74657320', '\x64617461');