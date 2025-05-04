// DOM elements
const tabs = document.querySelectorAll('.tab');
const charts = document.querySelectorAll('.chart');

// Add click event listeners to tabs
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const tabType = tab.getAttribute('data-tab');

    // Remove active class from all tabs and charts
    tabs.forEach(t => t.classList.remove('active'));
    charts.forEach(c => c.classList.remove('active'));

    // Add active class to clicked tab and corresponding chart
    tab.classList.add('active');
    document.getElementById(`${tabType}Chart`).classList.add('active');
  });
});

// Function to draw temperature chart line
function drawTemperatureLine() {
  const canvas = document.getElementById('tempCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const tempContainer = document.getElementById('temperatureChart');
  const values = [32, 31, 31, 28, 27, 26, 26, 29];

  // Get container dimensions
  const width = tempContainer.clientWidth;
  const height = tempContainer.clientHeight;

  // Set canvas dimensions
  canvas.width = width;
  canvas.height = height;

  // Set background color
  ctx.fillStyle = '#202025';
  ctx.fillRect(0, 0, width, height);

  // Calculate spacing and positions
  const padding = { left: 15, right: 15, top: 25, bottom: 20 };
  const chartWidth = width - padding.left - padding.right;
  const step = chartWidth / (values.length - 1);

  // Use fixed height scaling to match reference image
  const chartHeight = height - padding.top - padding.bottom;
  const baseY = padding.top + (chartHeight * 0.5);
  const yScale = chartHeight * 0.4;

  // Create points array to reuse for line and filling
  const points = [];

  values.forEach((temp, i) => {
    const x = padding.left + (i * step);

    // Scale temp value for height (higher temp = higher on chart = lower y value)
    const normalizedTemp = (temp - 26) / (32 - 26);
    const y = baseY - (normalizedTemp * yScale);

    points.push({ x, y, temp });
  });

  // Fill the area below the line
  ctx.beginPath();
  ctx.moveTo(points[0].x, height - padding.bottom);

  // Go to first point
  ctx.lineTo(points[0].x, points[0].y);

  // Connect all points
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  // Complete the path to bottom right then bottom left
  ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
  ctx.lineTo(points[0].x, height - padding.bottom);

  // Create gradient for the fill
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(249, 171, 0, 0.25)');
  gradient.addColorStop(1, 'rgba(249, 171, 0, 0.05)');
  ctx.fillStyle = gradient;
  ctx.fill();

  // Draw the temperature line
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.strokeStyle = '#f9ab00';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw dots on the temperature line
  points.forEach(point => {
    // Draw white dot with yellow border
    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = '#f9ab00';
    ctx.lineWidth = 1;
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.stroke();
  });

  // Draw temperature values on the line
  ctx.textAlign = 'center';
  ctx.font = '11px Roboto';
  ctx.fillStyle = '#ffffff';

  points.forEach(point => {
    // Draw the temperature value above the line
    ctx.fillText(point.temp, point.x, point.y - 10);
  });

  // Add the time markers
  const times = ['12:00', '15:00', '18:00', '21:00', '00:00', '03:00', '06:00', '09:00'];
  const timeMarkers = document.getElementById('timeMarkers');
  timeMarkers.innerHTML = '';

  times.forEach((time, i) => {
    const x = padding.left + (i * step);
    const marker = document.createElement('div');
    marker.className = 'time-marker';
    marker.textContent = time;
    marker.style.left = `${x}px`;
    timeMarkers.appendChild(marker);
  });
}

// Handle temperature unit toggle when clicking on degrees
const degreeElement = document.querySelector('.degree');
if (degreeElement) {
  degreeElement.addEventListener('click', () => {
    const currentUnit = degreeElement.textContent;
    const tempElements = document.querySelectorAll('.temperature, .temp-number');

    if (currentUnit === '°F') {
      // Convert to Celsius
      degreeElement.textContent = '°C';
      tempElements.forEach(el => {
        const fahrenheit = parseInt(el.textContent);
        const celsius = Math.round((fahrenheit - 32) * 5 / 9);
        el.textContent = celsius;
      });
    } else {
      // Convert to Fahrenheit
      degreeElement.textContent = '°F';
      tempElements.forEach(el => {
        const celsius = parseInt(el.textContent);
        const fahrenheit = Math.round(celsius * 9 / 5 + 32);
        el.textContent = fahrenheit;
      });
    }

    // Redraw temperature line after conversion
    drawTemperatureLine();
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  drawTemperatureLine();

  // Handle window resize
  window.addEventListener('resize', () => {
    drawTemperatureLine();
  });
});

// Add a hover effect for precipitation bars
const precipitationValues = document.querySelectorAll('.precipitation-value');
precipitationValues.forEach(value => {
  value.addEventListener('mouseenter', () => {
    value.style.transform = 'translateY(-3px)';
    value.style.color = '#4285f4';
  });

  value.addEventListener('mouseleave', () => {
    value.style.transform = '';
    value.style.color = '';
  });
});

// Add animation for wind arrows
const windValues = document.querySelectorAll('.wind-value');
windValues.forEach(value => {
  value.addEventListener('mouseenter', () => {
    const arrow = value.querySelector('.wind-arrow');
    if (arrow) {
      arrow.style.transform = 'translateY(-3px)';
    }
    value.style.color = '#70757a';
  });

  value.addEventListener('mouseleave', () => {
    const arrow = value.querySelector('.wind-arrow');
    if (arrow) {
      arrow.style.transform = '';
    }
    value.style.color = '';
  });
});
