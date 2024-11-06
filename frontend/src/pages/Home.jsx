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
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  const delayData = {
    labels: ['0-15', '15-30', '30-60', '60-120', '120+'],
    datasets: [{
      label: 'Delay Distribution (minutes)',
      data: [45, 25, 15, 10, 5],
      ...chartTheme.datasetStyles.bar
    }]
  };

  const growthData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
    datasets: [{
      label: 'Flight Frequency Growth',
      data: [100, 105, 108, 110, 112, 115],
      tension: 0.3,
      fill: true,
      ...chartTheme.datasetStyles.line
    }]
  };

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
      <h1 className="dashboard-title">Air Cargo Operations Overview</h1>
      
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
          <h2>Delay Distribution</h2>
          <div className="chart">
            <Bar data={delayData} options={chartTheme.defaultOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Weekly Growth Trend</h2>
          <div className="chart">
            <Line data={growthData} options={chartTheme.defaultOptions} />
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