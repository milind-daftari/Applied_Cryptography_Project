import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTable } from 'react-table';

const RentalQuery = () => {
    const [filter, setFilter] = useState('BHK');
    const [filterOptions, setFilterOptions] = useState([]);
    const [selectedOption, setSelectedOption] = useState('');
    const [data, setData] = useState([]);

    const columns = React.useMemo(
        () => [
            { Header: 'BHK', accessor: 'BHK' },
            { Header: 'Rent', accessor: 'Rent' },
            { Header: 'Size', accessor: 'Size' },
            { Header: 'Floor', accessor: 'Floor' },
            { Header: 'Area Type', accessor: 'AreaType' },
            { Header: 'Area Locality', accessor: 'AreaLocality' },
            { Header: 'City', accessor: 'City' },
            { Header: 'Furnishing Status', accessor: 'FurnishingStatus' },
            { Header: 'Tenant Preferred', accessor: 'TenantPreferred' },
            { Header: 'Bathroom', accessor: 'Bathroom' },
            { Header: 'Point of Contact', accessor: 'PointOfContact' }
        ],
        []
    );

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
    } = useTable({ columns, data });
    console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);

    useEffect(() => {
        // Fetch filter options based on selected filter category
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/filter-options?category=${filter}`)
            .then(response => {
                setFilterOptions(response.data.options);
                setSelectedOption(response.data.options[0]);
            })
            .catch(error => console.error('Error fetching filter options: ', error));
    }, [filter]);

    const fetchFilteredData = () => {
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/rental-data?filter=${filter}&value=${selectedOption}`)
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    };

    return (
        <div className="rental-query-container">
            <h1>Rental Price Query System</h1>
            <div className="filter-section">
                <select value={filter} onChange={e => setFilter(e.target.value)}>
                    <option value="BHK">BHK</option>
                    <option value="Rent">Rent</option>
                    <option value="Size">Size</option>
                    <option value="Floor">Floor</option>
                    <option value="Area Type">Area Type</option>
                    <option value="Area Locality">Area Locality</option>
                    <option value="City">City</option>
                    <option value="Furnishing Status">Furnishing Status</option>
                    <option value="Tenant Preferred">Tenant Preferred</option>
                    <option value="Bathroom">Bathroom</option>
                    <option value="Point of Contact">Point of Contact</option>
                </select>
                <select value={selectedOption} onChange={e => setSelectedOption(e.target.value)}>
                    {filterOptions.map(option => (
                        <option key={option} value={option}>{option}</option>
                    ))}
                </select>
                <button onClick={fetchFilteredData}>Fetch Data</button>
            </div>
            <div className="data-table">
                <table {...getTableProps()}>
                    <thead>
                        {headerGroups.map(headerGroup => (
                            <tr {...headerGroup.getHeaderGroupProps()}>
                                {headerGroup.headers.map(column => (
                                    <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody {...getTableBodyProps()}>
                        {rows.map((row, i) => {
                            prepareRow(row);
                            return (
                                <tr {...row.getRowProps()}>
                                    {row.cells.map(cell => {
                                        return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>;
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default RentalQuery;
