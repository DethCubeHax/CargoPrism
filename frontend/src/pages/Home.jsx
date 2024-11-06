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
    labels: [],
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
              data: data.ALL_weekly_cod_percentag,
              ...chartTheme.datasetStyles.bar
            }
          ]
        });
        setTop10Data({
          labels: data.Name_top_10,
          datasets: [
            {
              label: 'Top 10 Routes',
              data: data.Value_top_10,
              ...chartTheme.datasetStyles.bar
            }
          ]
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
            <Bar data={top10Data} options={chartTheme.defaultOptions} />
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