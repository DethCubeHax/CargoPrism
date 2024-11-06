const chartTheme = {
    colors: {
      jade: 'rgb(0, 101, 100)',         // Cathay Jade (Primary)
      mediumJade: 'rgb(54, 125, 121)',  // Medium Jade (Secondary)
      lightJade: 'rgb(100, 150, 147)',  // Lighter variant
      paleJade: 'rgb(150, 185, 183)',   // Pale variant
      mist: 'rgb(200, 220, 219)',       // Very light variant
      white: 'rgb(255, 255, 255)',
      slate: 'rgb(235, 237, 236)',      // Light Slate for backgrounds
    },
  
    datasetStyles: {
      bar: {
        backgroundColor: 'rgb(0, 101, 100)',
        hoverBackgroundColor: 'rgb(54, 125, 121)',
      },
      
      line: {
        borderColor: 'rgb(0, 101, 100)',
        backgroundColor: 'rgba(0, 101, 100, 0.1)',
        pointBackgroundColor: 'rgb(54, 125, 121)',
        pointBorderColor: 'rgb(0, 101, 100)',
        pointHoverBackgroundColor: 'rgb(0, 101, 100)',
        pointHoverBorderColor: 'rgb(54, 125, 121)',
      },
      
      pie: {
        backgroundColor: [
          'rgb(0, 101, 100)',    // Jade
          'rgb(54, 125, 121)',   // Medium Jade
          'rgb(100, 150, 147)',  // Light Jade
        ],
        hoverBackgroundColor: [
          'rgb(54, 125, 121)',   // Medium Jade
          'rgb(100, 150, 147)',  // Light Jade
          'rgb(150, 185, 183)',  // Pale Jade
        ],
      }
    },
  
    defaultOptions: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: 'rgb(0, 101, 100)',
            font: {
              weight: 'bold'
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 101, 100, 0.1)'
          },
          ticks: {
            color: 'rgb(0, 101, 100)'
          }
        },
        y: {
          grid: {
            color: 'rgba(0, 101, 100, 0.1)'
          },
          ticks: {
            color: 'rgb(0, 101, 100)'
          }
        }
      }
    }
  };
  
  export default chartTheme;