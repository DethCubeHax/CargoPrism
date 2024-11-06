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
  const totalPages = Math.ceil(data.datasets.length / rowsPerPage);

  const getCurrentPageData = () => {
    const start = currentPage * rowsPerPage;
    return data.datasets.slice(start, start + rowsPerPage);
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
            const date = row[0];
            const top5 = row.slice(1, 6);
            
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

  useEffect(() => {
    fetch('http://localhost:8000/overview', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => {
        console.log('Raw Response:', response);
        return response.json();
      })
      .then(data => {
        console.log('Received data:', data);
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

        // Parse the weekly_top_10 JSON string
        const top10 = JSON.parse(data.weekly_top_10);
        
        // Now you can access the columns
        const columns = ["Date", ...top10.columns];

        // Formatting data by combining dates with data entries
        const formattedData = top10.index.map((date, index) => {
          return [date, ...top10.data[index]];
        });

        setTop10Data({
          labels: columns,
          datasets: formattedData
        });
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  const cancellationData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Cancellation Rate (%)',
      data: [2.1, 1.8, 2.5, 1.9, 2.2, 1.5, 1.7],
      tension: 0.3,
      fill: true,
      ...chartTheme.datasetStyles.line
    }]
  };

  return (
    <div className="detail-wrapper">
      <h1 className="dashboard-title">Air Cargo Operations Weekly Overview</h1>
      
      <div className="metrics-container">
        <div className="metrics">
          <div className="metric-item">
            <h3>Total Flights</h3>
            <p className="metric-value">1,234</p>
          </div>
          <div className="metric-item">
            <h3>On-time Performance</h3>
            <p className="metric-value">92.5%</p>
          </div>
          <div className="metric-item">
            <h3>Active Routes</h3>
            <p className="metric-value">28</p>
          </div>
          <div className="metric-item">
            <h3>Cancellation Rate</h3>
            <p className="metric-value">2.1%</p>
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
          <h2>Daily Cancellation Rate</h2>
          <div className="chart">
            <Line data={cancellationData} options={chartTheme.defaultOptions} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;