import React, { useState } from 'react';
import axios from 'axios';

const RentalQuery = () => {
    const [bhk, setBHK] = useState('');
    const [city, setCity] = useState('');
    const [furnishingStatus, setFurnishingStatus] = useState('');
    const [bathroom, setBathroom] = useState('');
    const [averageRent, setAverageRent] = useState('');

    const handleFetchData = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/filter-options`, {
                params: { bhk, city, furnishingStatus, bathroom }
            });
            setAverageRent(response.data.averageRent);
        }
        catch(error){
            console.error('Error fetching data: ', error);
        }
    };

    const containerStyle = {
        padding: '20px',
        fontFamily: 'Arial, sans-serif'
    };

    const filterContainerStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginBottom: '20px'
    };

    const selectStyle = {
        marginBottom: '10px',
        padding: '10px',
        width: '200px'
    };

    const buttonStyle = {
        padding: '10px 20px',
        backgroundColor: '#007BFF',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        width: '220px'  // Slightly wider to account for padding in selects
    };

    const resultStyle = {
        marginTop: '20px',
        fontWeight: 'bold',
        fontSize: '24px',
        color: '#333'
    };

    return (
        <div style={containerStyle}>
            <h1>Rental Price Query System</h1>
            <div style={filterContainerStyle}>
                <select style={selectStyle} value={bhk} onChange={e => setBHK(e.target.value)}>
                    <option value="">Select BHK</option>
                    {[1,2,3,4,5,6].map(b => <option key={b} value={b}>{b}</option>)}
                </select>
                <select style={selectStyle} value={city} onChange={e => setCity(e.target.value)}>
                    <option value="">Select City</option>
                    {["Bangalore", "Kolkata", "Chennai", "Delhi", "Hyderabad", "Mumbai"].map(city => <option key={city} value={city}>{city}</option>)}
                </select>
                <select style={selectStyle} value={furnishingStatus} onChange={e => setFurnishingStatus(e.target.value)}>
                    <option value="">Select Furnishing Status</option>
                    {["Unfurnished", "Semi-Furnished", "Furnished"].map(status => <option key={status} value={status}>{status}</option>)}
                </select>
                <select style={selectStyle} value={bathroom} onChange={e => setBathroom(e.target.value)}>
                    <option value="">Select Bathroom</option>
                    {[1,2,3,4,5,6,7,10].map(b => <option key={b} value={b}>{b}</option>)}
                </select>
                <button style={buttonStyle} onClick={handleFetchData}>Fetch Data</button>
            
            {averageRent && <div style={resultStyle}>Average Rent: {averageRent}</div>}
        </div>
        </div>
    );
};

export default RentalQuery;
