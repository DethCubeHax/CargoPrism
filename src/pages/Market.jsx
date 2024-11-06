import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import chartTheme from '../config/chartTheme';
import './Market.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function MarketAnalysis() {
  const marketShareData = {
    labels: ['CX', 'KA', 'SQ', 'TG', 'VN', 'Others'],
    datasets: [{
      data: [35, 20, 15, 12, 8, 10],
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#C9CBCF'
      ],
      ...chartTheme.datasetStyles.doughnut
    }]
  };

  const routeAnalysisData = {
    labels: ['HKG-NRT', 'HKG-ICN', 'HKG-SIN', 'HKG-BKK', 'HKG-PVG'],
    datasets: [
      {
        label: 'Our Frequency',
        data: [45, 35, 40, 30, 25],
        ...chartTheme.datasetStyles.bar
      },
      {
        label: 'Competitor Average',
        data: [40, 30, 35, 28, 22],
        ...chartTheme.datasetStyles.bar
      }
    ]
  };

  const marketTrendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Market Size (Flights)',
        data: [250, 260, 270, 280, 290, 300],
        ...chartTheme.datasetStyles.line
      },
      {
        label: 'Our Share (%)',
        data: [35, 36, 35, 37, 38, 39],
        yAxisID: 'percentage',
        ...chartTheme.datasetStyles.line
      }
    ]
  };

  const regionalShareData = {
    labels: ['Northeast Asia', 'Southeast Asia', 'South Asia', 'Australia', 'Others'],
    datasets: [{
      data: [40, 30, 15, 10, 5],
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#C9CBCF'
      ],
      ...chartTheme.datasetStyles.doughnut
    }]
  };

  return (
    <div className="market-analysis-wrapper">
      <div className="market-header">
        <h1>Market Analysis</h1>
        <div className="period-selector">
          {/* Period selector components will go here */}
        </div>
      </div>

      <div className="market-metrics">
        <div className="metric-card">
          <h3>Market Share</h3>
          <p className="metric-value">35.2%</p>
          <p className="metric-change positive">+2.1%</p>
        </div>
        <div className="metric-card">
          <h3>Routes Served</h3>
          <p className="metric-value">28</p>
          <p className="metric-change positive">+2</p>
        </div>
        <div className="metric-card">
          <h3>Competitor Count</h3>
          <p className="metric-value">12</p>
          <p className="metric-change neutral">No change</p>
        </div>
        <div className="metric-card">
          <h3>Market Growth</h3>
          <p className="metric-value">8.5%</p>
          <p className="metric-change positive">+1.2%</p>
        </div>
      </div>

      <div className="market-grid">
        <div className="chart-container">
          <h2>Market Share by Carrier</h2>
          <div className="chart donut-chart">
            <Doughnut data={marketShareData} options={{
              ...chartTheme.defaultOptions,
              maintainAspectRatio: false
            }} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Regional Distribution</h2>
          <div className="chart donut-chart">
            <Doughnut data={regionalShareData} options={{
              ...chartTheme.defaultOptions,
              maintainAspectRatio: false
            }} />
          </div>
        </div>

        <div className="chart-container full-width">
          <h2>Route Frequency Analysis</h2>
          <div className="chart">
            <Bar data={routeAnalysisData} options={chartTheme.defaultOptions} />
          </div>
        </div>

        <div className="chart-container full-width">
          <h2>Market Trend Analysis</h2>
          <div className="chart">
            <Line 
              data={marketTrendData} 
              options={{
                ...chartTheme.defaultOptions,
                scales: {
                  percentage: {
                    position: 'right',
                    min: 0,
                    max: 100,
                    ticks: {
                      callback: function(value) {
                        return value + '%';
                      }
                    }
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default MarketAnalysis;