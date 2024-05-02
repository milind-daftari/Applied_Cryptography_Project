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
- Docker (https://www.docker.com/)
- Git (optional, if you plan to clone the repository)

### Setting Up the Environment

#### Docker Setup

1. Clone the repository or download the source code.
2. From the project root directory, build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```
   This command will set up both the front end and the back end services.

#### Back End Setup

1. Navigate to the Flask project directory:
   ```bash
   cd backend/crypto_project
   ```
2. Create a virtual environment and activate it (optional if running outside Docker):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
   ```
3. Install the required Python packages:
   ```bash
   pip install flask flask-cors
   ```

#### Front End Setup

1. Navigate to the React project directory (optional if running inside Docker):
   ```bash
   cd rental-query-app
   ```
2. Install the required Node modules:
   ```bash
   npm install
   ```

### Running the Application

The application should be accessible via:

- **Front End**: `http://localhost:3000`
- **Back End**: `http://localhost:5000`

## Usage

- **Select a Filter**: Use the first dropdown on the React UI to select a category (e.g., BHK, City).
- **Choose an Option**: After selecting a category, the second dropdown will populate with options. Select one that matches your criteria.
- **Fetch Data**: Click the "Fetch Data" button to retrieve the rental data based on the selected filter and option. The results will be displayed in a table below the filters.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Any contributions you make are **greatly appreciated**.
