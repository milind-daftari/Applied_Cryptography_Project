# Rental Price Query System

This project provides a privacy-preserving rental price query system using React for the front end and Flask for the back end. The system allows users to select rental property characteristics and receive aggregated data without exposing their search details.

## Project Structure

- **Front End**: Implemented in React, housed in the `rental-query-app` folder, providing an interactive UI for users to specify their search criteria.
- **Back End**: Built with Flask, located in the `backend/crypto_project` folder, handles API requests, performs secure queries on the data, and returns results.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have the following installed on your system:

- Node.js and npm (https://nodejs.org/)
- Python 3 (https://www.python.org/downloads/)
- Git (optional, if you plan to clone the repository)

### Setting Up the Environment

#### Back End Setup

1. Clone the repository or download the source code.
2. Navigate to the Flask project directory:
   ```bash
   cd backend/crypto_project
   ```
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the required Python packages:
   ```bash
   pip install flask flask-cors
   ```

#### Front End Setup

1. Navigate to the React project directory:
   ```bash
   cd rental-query-app
   ```
2. Install the required Node modules:
   ```bash
   npm install
   ```

### Running the Application

#### Running the Back End

1. Within the `backend/crypto_project` directory, start the Flask application:
   ```bash
   python app.py
   ```
   This will serve the API on `http://localhost:5000`.

#### Running the Front End

1. In a new terminal, navigate to the `rental-query-app` directory and start the React application:
   ```bash
   npm start
   ```
   This will run the front end on `http://localhost:3000` and should automatically open in your default web browser.

## Usage

- **Select a Filter**: Use the first dropdown on the React UI to select a category (e.g., BHK, City).
- **Choose an Option**: After selecting a category, the second dropdown will populate with options. Select one that matches your criteria.
- **Fetch Data**: Click the "Fetch Data" button to retrieve the rental data based on the selected filter and option. The results will be displayed in a table below the filters.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Any contributions you make are **greatly appreciated**.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

## Acknowledgments

- Thanks to all the contributors who have invested their time into improving this project.
