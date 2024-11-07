import React from 'react';
import { useState, useEffect } from 'react';
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
  const [metrics, setMetrics] = useState({
    daily_flights: { value: 0, change: 0 },
    ontime_performance: { value: 0, change: 0 },
    avg_delay: { value: 0, change: 0 },
    completion_factor: { value: 0, change: 0 }
  });
  
  const [scheduleChanges, setScheduleChanges] = useState({
    columns: [],
    data: []
  });

  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 3;

  useEffect(() => {
    fetch('http://localhost:8000/performance', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setMetrics(data.metrics);
        setScheduleChanges(data.schedule_changes);
      })
      .catch(error => {
        console.error('Error fetching performance data:', error);
      });
  }, []);

  const renderScheduleChangesTable = () => {
    if (scheduleChanges.data[0] === "None") {
      return (
        <tr>
          <td colSpan={scheduleChanges.columns.length} style={{textAlign: 'center', padding: '20px'}}>
            No cancelled flights resumed in this period
          </td>
        </tr>
      );
    }

    const startIdx = currentPage * rowsPerPage;
    const endIdx = startIdx + rowsPerPage;
    const totalPages = Math.ceil(scheduleChanges.data.length / rowsPerPage);
    const currentData = scheduleChanges.data.slice(startIdx, endIdx);

    return (
      <>
        {currentData.map((row, index) => (
          <tr key={index}>
            {row.map((cell, cellIndex) => (
              <td key={cellIndex}>{cell}</td>
            ))}
          </tr>
        ))}
        <tr>
          <td colSpan={scheduleChanges.columns.length} className="pagination-row">
            <div className="pagination-controls">
              <button 
                onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                disabled={currentPage === 0}
                className="pagination-button"
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {currentPage + 1} of {totalPages}
              </span>
              <button 
                onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                disabled={currentPage === totalPages - 1}
                className="pagination-button"
              >
                Next
              </button>
            </div>
          </td>
        </tr>
      </>
    );
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
          <p className="metric-value">{metrics.daily_flights.value}</p>
          <p className={`metric-change ${metrics.daily_flights.change >= 0 ? 'positive' : 'negative'}`}>
            {metrics.daily_flights.change >= 0 ? '+' : ''}{metrics.daily_flights.change}%
          </p>
        </div>
        <div className="metric-card">
          <h3>On-time Performance</h3>
          <p className="metric-value">{metrics.ontime_performance.value}%</p>
          <p className={`metric-change ${metrics.ontime_performance.change >= 0 ? 'positive' : 'negative'}`}>
            {metrics.ontime_performance.change >= 0 ? '+' : ''}{metrics.ontime_performance.change}%
          </p>
        </div>
        <div className="metric-card">
          <h3>Avg Delay Time</h3>
          <p className="metric-value">{metrics.avg_delay.value}min</p>
          <p className={`metric-change ${metrics.avg_delay.change <= 0 ? 'positive' : 'negative'}`}>
            {metrics.avg_delay.change >= 0 ? '+' : ''}{metrics.avg_delay.change}min
          </p>
        </div>
        <div className="metric-card">
          <h3>Completion Factor</h3>
          <p className="metric-value">{metrics.completion_factor.value}%</p>
          <p className={`metric-change ${metrics.completion_factor.change >= 0 ? 'positive' : 'negative'}`}>
            {metrics.completion_factor.change >= 0 ? '+' : ''}{metrics.completion_factor.change}%
          </p>
        </div>
      </div>

      <div className="schedule-changes">
        <h2>Competitors Flight Resumption Tracker</h2>
        <table className="schedule-table">
          <thead>
            <tr>
              {scheduleChanges.columns.map((column, index) => (
                <th key={index}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {renderScheduleChangesTable()}
          </tbody>
        </table>
      </div>

      <div className="charts-grid">
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