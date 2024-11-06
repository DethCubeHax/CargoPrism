import React from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
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
import styled from 'styled-components';

// Register ChartJS components
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

function Home() {
  // Sample data for bar chart
  const barData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Monthly Shipments',
      data: [65, 59, 80, 81, 56, 55],
      backgroundColor: '#89CBF3',
    }]
  };

  // Sample data for line graph
  const lineData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [{
      label: 'On-time Delivery Rate',
      data: [85, 88, 92, 95],
      borderColor: '#4299E1',
      tension: 0.1
    }]
  };

  // Sample data for pie chart
  const pieData = {
    labels: ['Air', 'Sea', 'Land'],
    datasets: [{
      data: [30, 50, 20],
      backgroundColor: ['#BEE3F8', '#4299E1', '#2B6CB0'],
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    }
  };

  return (
    <DetailWrapper>
      <h1 className="dashboard-title">Logistics Overview</h1>
      
      <div className="dashboard-grid">
        <div className="chart-container">
          <h2>Monthly Shipments</h2>
          <div className="chart">
            <Bar data={barData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Delivery Performance</h2>
          <div className="chart">
            <Line data={lineData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h2>Transport Mode Distribution</h2>
          <div className="chart">
            <Pie data={pieData} options={chartOptions} />
          </div>
        </div>

        <div className="metrics-container">
          <h2>Key Metrics</h2>
          <div className="metrics">
            <div className="metric-item">
              <h3>Total Shipments</h3>
              <p className="metric-value">1,234</p>
            </div>
            <div className="metric-item">
              <h3>On-time Delivery</h3>
              <p className="metric-value">95%</p>
            </div>
            <div className="metric-item">
              <h3>Active Routes</h3>
              <p className="metric-value">28</p>
            </div>
          </div>
        </div>
      </div>
    </DetailWrapper>
  );
}

const DetailWrapper = styled.div`
  padding: 2rem;

  .dashboard-title {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 2rem;
    color: #2D3748;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .chart-container {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);

    h2 {
      font-size: 1.2rem;
      margin-bottom: 1rem;
      color: #4A5568;
    }
  }

  .chart {
    height: 300px;
  }

  .metrics-container {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);

    h2 {
      font-size: 1.2rem;
      margin-bottom: 1rem;
      color: #4A5568;
    }
  }

  .metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .metric-item {
    text-align: center;
    
    h3 {
      font-size: 0.9rem;
      color: #718096;
      margin-bottom: 0.5rem;
    }

    .metric-value {
      font-size: 1.5rem;
      font-weight: bold;
      color: #2D3748;
    }
  }

  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
    
    .metrics {
      grid-template-columns: 1fr;
    }
  }
`;

export default Home;