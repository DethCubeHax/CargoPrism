import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import chartTheme from '../config/chartTheme';
import './Home.css';
import { useState, useEffect } from 'react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function DataTable({ data }) {
  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 4;

  const sortedDatasets = [...data.datasets].reverse();
  const totalPages = Math.ceil(sortedDatasets.length / rowsPerPage);

  const getCurrentPageData = () => {
    const start = currentPage * rowsPerPage;
    return sortedDatasets.slice(start, start + rowsPerPage);
  };

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Week</th>
            <th>No.1</th>
            <th>No.2</th>
            <th>No.3</th>
            <th>No.4</th>
            <th>No.5</th>
          </tr>
        </thead>
        <tbody>
          {getCurrentPageData().map((row, index) => {
            const rowData = row.slice(0, 6);
            const date = rowData[0];
            const top5 = rowData.slice(1);
            
            return (
              <tr key={index}>
                <td>{date}</td>
                {top5.map((airline, i) => (
                  <td key={i}>{airline}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="pagination">
        <button 
          className="pagination-button"
          onClick={() => setCurrentPage(prev => prev - 1)}
          disabled={currentPage === 0}
        >
          Previous
        </button>
        <span className="page-info">
          Page {currentPage + 1} of {totalPages}
        </span>
        <button 
          className="pagination-button"
          onClick={() => setCurrentPage(prev => prev + 1)}
          disabled={currentPage >= totalPages - 1}
        >
          Next
        </button>
      </div>
    </div>
  );
}

function Home() {
  const [metrics, setMetrics] = useState({
    total_flights: 0,
    ontime_performance: 0,
    active_routes: 0,
    cancellation_rate: 0
  });

  const [filters, setFilters] = useState({
    origin: '',
    destination: ''
  });

  const [stations, setStations] = useState({
    origins: [],
    destinations: []
  });

  const [rawData, setRawData] = useState(null);
  const [frequencyData, setFrequencyData] = useState({
    labels: [],
    datasets: []
  });

  const [performanceData, setPerformanceData] = useState({
    labels: [],
    datasets: []
  });

  const [top10Data, setTop10Data] = useState({
    labels: ['Week', 'No.1', 'No.2', 'No.3', 'No.4', 'No.5'],
    datasets: []
  });

  const [top5Data, setTop5Data] = useState({
    labels: ['Week', 'No.1', 'No.2', 'No.3', 'No.4', 'No.5'],
    datasets: []
  });

  const fetchData = (currentFilters) => {
    let url = 'http://localhost:8000/overview';
    const params = new URLSearchParams();
    if (currentFilters.origin) params.append('origin', currentFilters.origin);
    if (currentFilters.destination) params.append('destination', currentFilters.destination);
    if (params.toString()) url += `?${params.toString()}`;

    fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setRawData(data);
        setStations(data.stations);
        updateFilteredData(data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  };

  useEffect(() => {
    fetchData(filters);
  }, []);

  const updateFilteredData = (data) => {
    if (!data) return;

    setMetrics(data.metrics);

    setFrequencyData({
      labels: data.dates,
      datasets: [
        {
          label: 'CX',
          data: data.CX_weekly_fq,
          backgroundColor: 'rgb(0, 101, 100)',
          borderColor: 'rgb(0, 101, 100)',
          ...chartTheme.datasetStyles.bar
        },
        {
          label: 'All',
          data: data.ALL_weekly_fq,
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          ...chartTheme.datasetStyles.bar
        }
      ]
    });

    setPerformanceData({
      labels: data.dates,
      datasets: [
        {
          label: 'CX',
          data: data.CX_weekly_cod_percentage,
          ...chartTheme.datasetStyles.bar
        },
        {
          label: 'All',
          data: data.ALL_weekly_cod_percentage,
          ...chartTheme.datasetStyles.bar
        }
      ]
    });

    const top10 = JSON.parse(data.weekly_top_10);
    const columns = ["Date", ...top10.columns];
    const formattedTop10Data = top10.index.map((date, index) => {
      return [date, ...top10.data[index]];
    });
    setTop10Data({
      labels: columns,
      datasets: formattedTop10Data
    });

    const top5 = JSON.parse(data.weekly_top_5);
    const top5_columns = ["Date", ...top5.columns];
    const formattedTop5Data = top5.index.map((date, index) => {
      return [date, ...top5.data[index]];
    });
    setTop5Data({
      labels: top5_columns,
      datasets: formattedTop5Data
    });
  };

  const handleFilterChange = (filterType, value) => {
    const newFilters = {
      ...filters,
      [filterType]: value
    };
    setFilters(newFilters);
    fetchData(newFilters);
  };

  return (
    <div className="detail-wrapper">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Air Cargo Operations Weekly Overview</h1>
        <div className="filters-container">
          <div className="filter">
            <select 
              value={filters.origin}
              onChange={(e) => handleFilterChange('origin', e.target.value)}
            >
              <option value="">All Origins</option>
              {stations.origins.map(origin => (
                <option key={origin} value={origin}>{origin}</option>
              ))}
            </select>
          </div>
          <div className="filter">
            <select 
              value={filters.destination}
              onChange={(e) => handleFilterChange('destination', e.target.value)}
            >
              <option value="">All Destinations</option>
              {stations.destinations.map(dest => (
                <option key={dest} value={dest}>{dest}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      <div className="metrics-container">
        <div className="metrics">
          <div className="metric-item">
            <h3>Total Flights</h3>
            <p className="metric-value">{metrics.total_flights}</p>
          </div>
          <div className="metric-item">
            <h3>On-time Performance</h3>
            <p className="metric-value">{metrics.ontime_performance}%</p>
          </div>
          <div className="metric-item">
            <h3>Active Routes</h3>
            <p className="metric-value">{metrics.active_routes}</p>
          </div>
          <div className="metric-item">
            <h3>Cancellation Rate</h3>
            <p className="metric-value">{metrics.cancellation_rate}%</p>
          </div>
        </div>
      </div>
  
      <div className="dashboard-grid">
        <div className="chart-container">
          <h2>Flight Frequency by Carrier</h2>
          <div className="chart">
            <Line data={frequencyData} options={chartTheme.defaultOptions} />
          </div>
        </div>
  
        <div className="chart-container">
          <h2>Performance (Cancelled or Delayed)</h2>
          <div className="chart">
            <Line data={performanceData} options={chartTheme.defaultOptions} />
          </div>
        </div>
  
        <div className="chart-container">
          <h2>Weekly Top 10</h2>
          <div className="chart">
            <DataTable data={top10Data} />
          </div>
        </div>
  
        <div className="chart-container">
          <h2>Weekly Top 5</h2>
          <div className="chart">
            <DataTable data={top5Data} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;