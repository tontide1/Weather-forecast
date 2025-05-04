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

    // Re-draw the chart if it's the temperature tab
    if (tabType === 'temperature') {
      setTimeout(() => {
        drawTemperatureLine();
      }, 100);
    }
  });
});

// Function to draw temperature chart line
function drawTemperatureLine() {
  const tempValues = document.querySelectorAll('.temp-value');
  const temperaturePath = document.querySelector('.temperature-path');
  const temperatureArea = document.querySelector('.temperature-area');

  if (!temperaturePath || !temperatureArea || tempValues.length === 0) return;

  const values = Array.from(tempValues).map(el => {
    const tempNumber = parseInt(el.textContent || el.querySelector('.temp-number')?.textContent);
    return tempNumber;
  });

  const max = Math.max(...values) + 2; // Add 2 to give some top margin
  const min = Math.min(...values) - 2; // Subtract 2 to give some bottom margin
  const range = max - min;

  // Calculate points for the path
  let pathData = '';
  let areaData = '';

  tempValues.forEach((value, index) => {
    const tempNumber = parseInt(value.textContent || value.querySelector('.temp-number')?.textContent);
    const x = (index / (tempValues.length - 1)) * 100;
    const y = 100 - ((tempNumber - min) / range * 75); // Use 75% of height for better appearance

    if (index === 0) {
      pathData = `M${x},${y}`;
      areaData = `M${x},${y}`;
    } else {
      // Use quadratic curves for smoother lines
      const prevX = ((index - 1) / (tempValues.length - 1)) * 100;
      const controlX = (prevX + x) / 2;

      pathData += ` Q${controlX},${y} ${x},${y}`;
      areaData += ` L${x},${y}`;
    }
  });

  // Complete the area path - extend to bottom corners
  const lastX = 100;
  const lastY = 100;
  areaData += ` L${lastX},${lastY} L0,${lastY} Z`;

  temperaturePath.setAttribute('d', pathData);
  temperatureArea.setAttribute('d', areaData);

  // Animate the drawing of the path
  const pathLength = temperaturePath.getTotalLength();
  temperaturePath.style.strokeDasharray = pathLength;
  temperaturePath.style.strokeDashoffset = pathLength;

  setTimeout(() => {
    temperaturePath.style.transition = 'stroke-dashoffset 1.5s ease-in-out';
    temperaturePath.style.strokeDashoffset = 0;
  }, 100);
}

// Handle temperature unit toggle when clicking on degrees
const degreeElement = document.querySelector('.degree');
if (degreeElement) {
  degreeElement.addEventListener('click', () => {
    const currentUnit = degreeElement.textContent;
    const tempElements = document.querySelectorAll('.temperature, .temp-number, .temperature-values .temp-value');

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

// Add stars background animation
function createStars() {
  const body = document.body;
  for (let i = 0; i < 50; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.width = `${Math.random() * 2 + 1}px`;
    star.style.height = star.style.width;
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.animationDelay = `${Math.random() * 5}s`;
    body.appendChild(star);
  }
}

// Add hover effects for forecast items
function addForecastHoverEffects() {
  const forecastItems = document.querySelectorAll('.forecast-item');

  forecastItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      const siblings = Array.from(item.parentElement.children).filter(el => el !== item);
      siblings.forEach(sibling => {
        sibling.style.opacity = '0.7';
        sibling.style.transform = 'scale(0.98)';
      });
    });

    item.addEventListener('mouseleave', () => {
      const siblings = Array.from(item.parentElement.children);
      siblings.forEach(sibling => {
        sibling.style.opacity = '1';
        sibling.style.transform = '';
      });
    });
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  drawTemperatureLine();
  addForecastHoverEffects();

  // Animate container elements on page load
  const containers = document.querySelectorAll('.current-weather-container, .current-weather-status, .chart-container, .forecast-days');
  containers.forEach((container, index) => {
    container.style.opacity = '0';
    container.style.transform = 'translateY(20px)';

    setTimeout(() => {
      container.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      container.style.opacity = '1';
      container.style.transform = 'translateY(0)';
    }, 300 + (index * 150));
  });
});

// Add a hover effect for precipitation bars
const precipitationValues = document.querySelectorAll('.precipitation-value');
precipitationValues.forEach(value => {
  value.addEventListener('mouseenter', () => {
    value.style.transform = 'translateY(-5px)';
    value.style.color = '#bae6fd';
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
    value.style.color = '#7dd3fc';
  });

  value.addEventListener('mouseleave', () => {
    const arrow = value.querySelector('.wind-arrow');
    if (arrow) {
      arrow.style.transform = '';
    }
    value.style.color = '';
  });
});
