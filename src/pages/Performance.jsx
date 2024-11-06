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
import './Performance.css';

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

function Performance() {
  const monthlyFrequencyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: '2024',
        data: [150, 155, 160, 158, 162, 165, 170, 168, 172, 175, null, null],
        ...chartTheme.datasetStyles.line
      },
      {
        label: '2023',
        data: [140, 142, 145, 148, 150, 152, 155, 158, 160, 162, 165, 168],
        ...chartTheme.datasetStyles.line
      }
    ]
  };

  const routePerformanceData = {
    labels: ['HKG-NRT', 'HKG-ICN', 'HKG-SIN', 'HKG-BKK', 'HKG-PVG'],
    datasets: [
      {
        label: 'On-time Rate (%)',
        data: [92, 88, 95, 90, 87],
        ...chartTheme.datasetStyles.bar
      },
      {
        label: 'Utilization Rate (%)',
        data: [85, 82, 88, 84, 80],
        ...chartTheme.datasetStyles.bar
      }
    ]
  };

  const delayAnalysisData = {
    labels: ['Ground Handling', 'Weather', 'Technical', 'Air Traffic', 'Other'],
    datasets: [{
      label: 'Delay Causes (Hours)',
      data: [24, 36, 18, 30, 12],
      ...chartTheme.datasetStyles.bar
    }]
  };

  const weeklyComparisonData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Flights Operated',
        data: [45, 42, 47, 45, 48, 40, 38],
        ...chartTheme.datasetStyles.line
      },
      {
        label: 'Flights Scheduled',
        data: [48, 45, 48, 46, 50, 42, 40],
        ...chartTheme.datasetStyles.line
      }
    ]
  };

  return (
    <div className="performance-wrapper">
      <div className="performance-header">
        <h1>Performance Analytics</h1>
        <div className="period-selector">
          {/* Period selector components will go here */}
        </div>
      </div>

      <div className="metrics-overview">
        <div className="metric-card">
          <h3>Average Daily Flights</h3>
          <p className="metric-value">42.5</p>
          <p className="metric-change positive">+5.2%</p>
        </div>
        <div className="metric-card">
          <h3>On-time Performance</h3>
          <p className="metric-value">91.2%</p>
          <p className="metric-change positive">+2.1%</p>
        </div>
        <div className="metric-card">
          <h3>Avg Delay Time</h3>
          <p className="metric-value">18min</p>
          <p className="metric-change negative">+3min</p>
        </div>
        <div className="metric-card">
          <h3>Completion Factor</h3>
          <p className="metric-value">98.5%</p>
          <p className="metric-change positive">+0.5%</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container full-width">
          <h2>Monthly Frequency Trends</h2>
          <div className="chart">
            <Line data={monthlyFrequencyData} options={chartTheme.defaultOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Route Performance</h2>
          <div className="chart">
            <Bar data={routePerformanceData} options={chartTheme.defaultOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Delay Analysis</h2>
          <div className="chart">
            <Bar data={delayAnalysisData} options={chartTheme.defaultOptions} />
          </div>
        </div>

        <div className="chart-container full-width">
          <h2>Weekly Operation Comparison</h2>
          <div className="chart">
            <Line data={weeklyComparisonData} options={chartTheme.defaultOptions} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Performance;