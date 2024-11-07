import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { useState, useEffect } from 'react';
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
  const [metrics, setMetrics] = useState({
    market_share: { value: 0, change: 0 },
    routes_served: { value: 0, change: 0 },
    competitor_count: { value: 0, change: 0 },
    market_growth: { value: 0 }
  });

  useEffect(() => {
    fetch('http://localhost:8000/market-metrics', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setMetrics(data);
      })
      .catch(error => {
        console.error('Error fetching market metrics:', error);
      });
  }, []);

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
          <p className="metric-value">{metrics.market_share.value}%</p>
          <p className={`metric-change ${metrics.market_share.change >= 0 ? 'positive' : 'negative'}`}>
            {metrics.market_share.change >= 0 ? '+' : ''}{metrics.market_share.change}%
          </p>
        </div>
        <div className="metric-card">
          <h3>Routes Served</h3>
          <p className="metric-value">{metrics.routes_served.value}</p>
          <p className={`metric-change ${metrics.routes_served.change >= 0 ? 'positive' : 'negative'}`}>
            {metrics.routes_served.change >= 0 ? '+' : ''}{metrics.routes_served.change}
          </p>
        </div>
        <div className="metric-card">
          <h3>Competitor Count</h3>
          <p className="metric-value">{metrics.competitor_count.value}</p>
          <p className={`metric-change ${metrics.competitor_count.change === 0 ? 'neutral' : 
            metrics.competitor_count.change > 0 ? 'negative' : 'positive'}`}>
            {metrics.competitor_count.change === 0 ? 'No change' : 
             `${metrics.competitor_count.change > 0 ? '+' : ''}${metrics.competitor_count.change}`}
          </p>
        </div>
        <div className="metric-card">
          <h3>Market Growth</h3>
          <p className="metric-value">{metrics.market_growth.value}%</p>
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