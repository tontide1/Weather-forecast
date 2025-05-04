document.addEventListener('DOMContentLoaded', function() {
    fetchWeatherData();
});

async function fetchWeatherData() {
    try {
        const response = await fetch('/api/getdata/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        displayWeatherData(data);
    } catch (error) {
        console.error('Error fetching weather data:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

function displayWeatherData(data) {
    const weatherDataContainer = document.getElementById('weatherData');
    document.getElementById('loading').style.display = 'none';
    
    if (data.length === 0) {
        document.getElementById('error').textContent = 'No weather data available';
        document.getElementById('error').style.display = 'block';
        return;
    }

    weatherDataContainer.style.display = 'flex';
    
    // Group data by location
    const locationGroups = {};
    data.forEach(item => {
        if (!locationGroups[item.location]) {
            locationGroups[item.location] = [];
        }
        locationGroups[item.location].push(item);
    });
    
    // Create a card for each location
    for (const [location, items] of Object.entries(locationGroups)) {
        const locationCol = document.createElement('div');
        locationCol.className = 'col-md-6 mb-4';
        
        const card = document.createElement('div');
        card.className = 'card weather-card';
        
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header';
        cardHeader.innerHTML = `<h5>${location}</h5>`;
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        // Create a table for the weather data
        const table = document.createElement('table');
        table.className = 'table table-hover';
        
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Date</th>
                <th>Temperature (°C)</th>
                <th>Weather</th>
                <th>Humidity (%)</th>
            </tr>
        `;
        
        const tbody = document.createElement('tbody');
        
        // Add rows for each date
        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(item.date).toLocaleDateString()}</td>
                <td>${item.temp !== null ? item.temp : 'N/A'}</td>
                <td>${item.weather || 'N/A'}</td>
                <td>${item.rhum !== null ? item.rhum : 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
        
        table.appendChild(thead);
        table.appendChild(tbody);
        cardBody.appendChild(table);
        
        card.appendChild(cardHeader);
        card.appendChild(cardBody);
        locationCol.appendChild(card);
        weatherDataContainer.appendChild(locationCol);
    }
    
    // If we have temperature data for multiple days, create a chart
    createTemperatureChart(data);
}

function createTemperatureChart(data) {
    // Check if we have enough data for a meaningful chart
    if (data.length < 2) return;
    
    // Create a chart container
    const chartContainer = document.createElement('div');
    chartContainer.className = 'col-12 mt-4';
    chartContainer.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5>Temperature Trends</h5>
            </div>
            <div class="card-body">
                <canvas id="temperatureChart"></canvas>
            </div>
        </div>
    `;
    
    document.getElementById('weatherData').appendChild(chartContainer);
    
    // Group data by location for the chart
    const locations = [...new Set(data.map(item => item.location))];
    const datasets = locations.map(location => {
        const locationData = data.filter(item => item.location === location);
        return {
            label: location,
            data: locationData.map(item => item.temp),
            fill: false,
            borderColor: getRandomColor(),
            tension: 0.1
        };
    });
    
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.filter(item => item.location === locations[0])
                      .map(item => new Date(item.date).toLocaleDateString()),
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
