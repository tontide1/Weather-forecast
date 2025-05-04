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
  const values = [26, 26, 27, 29, 32, 31, 30, 28];

  // Get container dimensions
  const width = tempContainer.clientWidth;
  const height = tempContainer.clientHeight;

  // Set canvas dimensions
  canvas.width = width;
  canvas.height = height;

  // Set background color
  ctx.fillStyle = '#202025';
  ctx.fillRect(0, 0, width, height);

  // Padding giống như trong CSS
  const padding = { left: 0, right: 0, top: 25, bottom: 10 };

  // Tính toán chiều rộng cho điểm
  const chartWidth = width;
  const pointSpacing = chartWidth / 8;

  // Tạo mảng vị trí các điểm
  const positions = [];
  for (let i = 0; i < 8; i++) {
    // Vị trí điểm cách đều nhau
    const x = pointSpacing * (i + 0.5);
    positions.push(x);
  }

  // Tính toán chiều cao biểu đồ
  const chartHeight = height - padding.top - padding.bottom;
  const baseY = padding.top + (chartHeight * 0.5);
  const yScale = chartHeight * 0.4;

  // Tạo mảng điểm
  const points = [];
  values.forEach((temp, i) => {
    const x = positions[i];

    // Tính toán vị trí Y dựa trên nhiệt độ
    const normalizedTemp = (temp - 26) / (32 - 26);
    const y = baseY - (normalizedTemp * yScale);

    points.push({ x, y, temp });
  });

  // Tô màu bên dưới đường
  ctx.beginPath();
  ctx.moveTo(points[0].x, height - padding.bottom);
  ctx.lineTo(points[0].x, points[0].y);

  // Nối tất cả các điểm
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  // Đóng đường path
  ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
  ctx.lineTo(points[0].x, height - padding.bottom);

  // Tạo gradient màu cho phần tô
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(249, 171, 0, 0.25)');
  gradient.addColorStop(1, 'rgba(249, 171, 0, 0.05)');
  ctx.fillStyle = gradient;
  ctx.fill();

  // Vẽ đường nhiệt độ
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.strokeStyle = '#f9ab00';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Vẽ điểm trên đường nhiệt độ
  points.forEach(point => {
    // Vẽ điểm trắng với viền vàng
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

  // Vẽ giá trị nhiệt độ
  ctx.textAlign = 'center';
  ctx.font = '11px Roboto';
  ctx.fillStyle = '#ffffff';

  points.forEach(point => {
    ctx.fillText(point.temp, point.x, point.y - 10);
  });
}

// Function to draw precipitation chart line
function drawPrecipitationLine() {
  const canvas = document.getElementById('precipCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const precipContainer = document.getElementById('precipitationChart');
  const values = [10, 5, 10, 25, 75, 10, 10, 10]; // percentages

  // Get container dimensions
  const width = precipContainer.clientWidth;
  const height = precipContainer.clientHeight;

  // Set canvas dimensions
  canvas.width = width;
  canvas.height = height;

  // Set background color
  ctx.fillStyle = '#202025';
  ctx.fillRect(0, 0, width, height);

  // Padding giống như trong CSS
  const padding = { left: 0, right: 0, top: 25, bottom: 10 };

  // Tính toán chiều rộng cho điểm
  const chartWidth = width;
  const pointSpacing = chartWidth / 8;

  // Tạo mảng vị trí các điểm
  const positions = [];
  for (let i = 0; i < 8; i++) {
    // Vị trí điểm cách đều nhau
    const x = pointSpacing * (i + 0.5);
    positions.push(x);
  }

  // Tính toán chiều cao biểu đồ
  const chartHeight = height - padding.top - padding.bottom;
  const baseY = padding.top + (chartHeight * 0.5);
  const yScale = chartHeight * 0.4;

  // Tạo mảng điểm
  const points = [];
  values.forEach((value, i) => {
    const x = positions[i];

    // Tính toán vị trí Y dựa trên % lượng mưa (0-100%)
    const normalizedValue = value / 100;
    const y = baseY - (normalizedValue * yScale);

    points.push({ x, y, value });
  });

  // Tô màu bên dưới đường
  ctx.beginPath();
  ctx.moveTo(points[0].x, height - padding.bottom);
  ctx.lineTo(points[0].x, points[0].y);

  // Nối tất cả các điểm
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  // Đóng đường path
  ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
  ctx.lineTo(points[0].x, height - padding.bottom);

  // Tạo gradient màu cho phần tô
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(66, 133, 244, 0.25)');
  gradient.addColorStop(1, 'rgba(66, 133, 244, 0.05)');
  ctx.fillStyle = gradient;
  ctx.fill();

  // Vẽ đường lượng mưa
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.strokeStyle = '#4285f4';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Vẽ điểm trên đường lượng mưa
  points.forEach(point => {
    // Vẽ điểm trắng với viền xanh
    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = '#4285f4';
    ctx.lineWidth = 1;
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.stroke();
  });

  // Vẽ giá trị lượng mưa
  ctx.textAlign = 'center';
  ctx.font = '11px Roboto';
  ctx.fillStyle = '#ffffff';

  points.forEach(point => {
    ctx.fillText(point.value + '%', point.x, point.y - 10);
  });
}

// Function to draw wind chart line
function drawWindLine() {
  const canvas = document.getElementById('windCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const windContainer = document.getElementById('windChart');
  const values = [5, 6, 8, 10, 6, 5, 5, 6]; // km/h
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'S', 'N', 'N'];

  // Get container dimensions
  const width = windContainer.clientWidth;
  const height = windContainer.clientHeight;

  // Set canvas dimensions
  canvas.width = width;
  canvas.height = height;

  // Set background color
  ctx.fillStyle = '#202025';
  ctx.fillRect(0, 0, width, height);

  // Padding giống như trong CSS
  const padding = { left: 0, right: 0, top: 25, bottom: 10 };

  // Tính toán chiều rộng cho điểm
  const chartWidth = width;
  const pointSpacing = chartWidth / 8;

  // Tạo mảng vị trí các điểm
  const positions = [];
  for (let i = 0; i < 8; i++) {
    // Vị trí điểm cách đều nhau
    const x = pointSpacing * (i + 0.5);
    positions.push(x);
  }

  // Tính toán chiều cao biểu đồ
  const chartHeight = height - padding.top - padding.bottom;
  const baseY = padding.top + (chartHeight * 0.5);
  const yScale = chartHeight * 0.4;

  // Tạo mảng điểm
  const points = [];
  values.forEach((value, i) => {
    const x = positions[i];

    // Tính toán vị trí Y dựa trên tốc độ gió (0-10 km/h)
    const normalizedValue = value / 10;
    const y = baseY - (normalizedValue * yScale);

    points.push({ x, y, value, direction: directions[i] });
  });

  // Tô màu bên dưới đường
  ctx.beginPath();
  ctx.moveTo(points[0].x, height - padding.bottom);
  ctx.lineTo(points[0].x, points[0].y);

  // Nối tất cả các điểm
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  // Đóng đường path
  ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
  ctx.lineTo(points[0].x, height - padding.bottom);

  // Tạo gradient màu cho phần tô
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(112, 117, 122, 0.25)');
  gradient.addColorStop(1, 'rgba(112, 117, 122, 0.05)');
  ctx.fillStyle = gradient;
  ctx.fill();

  // Vẽ đường tốc độ gió
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);

  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }

  ctx.strokeStyle = '#70757a';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Vẽ điểm trên đường tốc độ gió
  points.forEach(point => {
    // Vẽ điểm trắng với viền xám
    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = '#70757a';
    ctx.lineWidth = 1;
    ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
    ctx.stroke();
  });

  // Vẽ giá trị tốc độ và hướng gió
  ctx.textAlign = 'center';
  ctx.font = '11px Roboto';
  ctx.fillStyle = '#ffffff';

  points.forEach(point => {
    ctx.fillText(point.value + ' km/h', point.x, point.y - 10);
    ctx.fillText(point.direction, point.x, point.y - 24);
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
  drawPrecipitationLine();
  drawWindLine();

  // Handle window resize
  window.addEventListener('resize', () => {
    drawTemperatureLine();
    drawPrecipitationLine();
    drawWindLine();
  });
});

// Handle tab changes to redraw charts when needed
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const tabType = tab.getAttribute('data-tab');
    if (tabType === 'temperature') {
      drawTemperatureLine();
    } else if (tabType === 'precipitation') {
      drawPrecipitationLine();
    } else if (tabType === 'wind') {
      drawWindLine();
    }
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
