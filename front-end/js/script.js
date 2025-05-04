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
  const tempValues = document.querySelectorAll('.temp-value');
  const temperaturePath = document.querySelector('.temperature-path');
  const temperatureArea = document.querySelector('.temperature-area');

  if (!temperaturePath || !temperatureArea || tempValues.length === 0) return;

  const values = Array.from(tempValues).map(el => {
    const tempNumber = parseInt(el.querySelector('.temp-number').textContent);
    return tempNumber;
  });

  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min;

  // Calculate points for the path
  let pathData = '';
  let areaData = '';

  tempValues.forEach((value, index) => {
    const tempNumber = parseInt(value.querySelector('.temp-number').textContent);
    const x = (index / (tempValues.length - 1)) * 100;
    const y = 100 - ((tempNumber - min) / (range || 1)) * 80;

    if (index === 0) {
      pathData = `M${x},${y}`;
      areaData = `M${x},${y}`;
    } else {
      pathData += ` L${x},${y}`;
      areaData += ` L${x},${y}`;
    }

    // Position the temp dots
    value.style.left = `${x}%`;

    // Calculate y position (invert and scale)
    value.style.top = `${y}%`;
  });

  // Complete the area path
  areaData += ` L100,100 L0,100 Z`;

  temperaturePath.setAttribute('d', pathData);
  temperatureArea.setAttribute('d', areaData);
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
