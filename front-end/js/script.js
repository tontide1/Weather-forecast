// Hàm để vẽ biểu đồ và hiển thị dữ liệu
let weatherData = [];
let currentIndex = 0;
const daysToShow = 5; // Hiển thị 5 ngày
let chartInstance = null;
let isDragging = false;
let startX = 0;
let dragSensitivity = 50; // Độ nhạy khi kéo (pixel)
let currentDatabase = "database.json"; // Mặc định là Hà Nội

// Hàm lấy biểu tượng thời tiết
function getWeatherIcon(weather) {
  const icons = {
    sunny: "☀️",
    rain: "🌧️",
    cloudy: "☁️",
    "partly cloudy": "⛅",
    thunderstorm: "⛈️",
    snow: "❄️",
    mist: "🌫️",
  };
  return icons[weather.toLowerCase()] || "⛅";
}

// Hàm định dạng ngày
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

// Hàm lấy màu dựa trên nhiệt độ
function getTemperatureColor(temp) {
  if (temp <= 0) return "#00ffff";
  if (temp <= 10) return "#4a90e2";
  if (temp <= 20) return "#50c878";
  if (temp <= 30) return "#ffa500";
  return "#ff4500";
}

// Hàm chuyển đổi hướng gió thành mũi tên
function getWindDirectionArrow(direction) {
  const arrows = {
    N: "↑",
    NE: "↗",
    E: "→",
    SE: "↘",
    S: "↓",
    SW: "↙",
    W: "←",
    NW: "↖",
  };
  return arrows[direction] || direction;
}

// Hàm cập nhật thông tin thời tiết hiện tại
function updateCurrentWeather(date) {
  // Tìm dữ liệu thời tiết cho ngày được chọn
  const currentData = weatherData.find(
    (data) => formatDate(data.date) === date
  );

  if (currentData) {
    // Cập nhật các thông tin
    document.getElementById(
      "currentTemp"
    ).textContent = `${currentData.highTemperature}°C`;
    document.getElementById("currentWeather").textContent = getWeatherText(
      currentData.weather
    );
    document.getElementById(
      "currentWindSpeed"
    ).textContent = `${currentData.windSpeed} km/h`;
    document.getElementById("currentWindDirection").textContent =
      currentData.windDirection;
    document.querySelector(".weather-icon").textContent = getWeatherIcon(
      currentData.weather
    );
    document.getElementById("currentDate").textContent = formatDate(
      currentData.date
    );
    document.getElementById("currentChanceRain").textContent =
      currentData.chance_rain;
  }
}

// Hàm chuyển đổi mã thời tiết thành text
function getWeatherText(code) {
  const weatherTypes = {
    sunny: "Sunny",
    partlyCloudy: "Partly Cloudy",
    cloudy: "Cloudy",
    rainy: "Rainy",
    thunderstorm: "Thunderstorm",
    snowy: "Snowy",
    foggy: "Foggy",
  };
  return weatherTypes[code] || code;
}

// Hàm xử lý khi người dùng chọn khu vực
function handleLocationChange() {
  const locationSelect = document.getElementById("locationSelect");
  currentDatabase = locationSelect.value;
  loadWeatherData();
}

async function loadWeatherData() {
  try {
    const response = await fetch(`./assets/data/${currentDatabase}`);
    if (!response.ok) {
      throw new Error(`Không thể tải dữ liệu từ ${currentDatabase}`);
    }
    weatherData = await response.json();

    // Lấy ngày hiện tại (15/04/2025)
    const targetDate = "2025-04-15";

    // Tìm vị trí của ngày hiện tại trong dữ liệu
    const targetIndex = weatherData.findIndex(
      (data) => data.date === targetDate
    );

    if (targetIndex === -1) {
      throw new Error("Không tìm thấy ngày được chọn trong dữ liệu");
    }

    // Tính toán vị trí bắt đầu để ngày hiện tại nằm giữa
    currentIndex = Math.max(0, targetIndex - Math.floor(daysToShow / 2));

    // Đảm bảo luôn đủ 5 ngày để hiển thị
    if (currentIndex + daysToShow > weatherData.length) {
      currentIndex = Math.max(0, weatherData.length - daysToShow);
    }

    // Lấy dữ liệu thời tiết cho ngày hiện tại
    const currentWeather = weatherData[targetIndex];

    // Cập nhật thông tin thời tiết hiện tại
    document.getElementById(
      "currentTemp"
    ).textContent = `${currentWeather.highTemperature}°C`;
    document.getElementById("currentWeather").textContent = getWeatherText(
      currentWeather.weather
    );
    document.getElementById(
      "currentWindSpeed"
    ).textContent = `${currentWeather.windSpeed} km/h`;
    document.getElementById("currentWindDirection").textContent =
      currentWeather.windDirection;
    document.querySelector(".weather-icon").textContent = getWeatherIcon(
      currentWeather.weather
    );
    document.getElementById("currentDate").textContent = formatDate(
      currentWeather.date
    );
    document.getElementById("currentChanceRain").textContent =
      currentWeather.chance_rain;

    // Cập nhật biểu đồ
    updateChart();

    // Thêm sự kiện kéo cho biểu đồ
    const chartContainer = document.querySelector(".chart-container");
    const canvas = document.getElementById("temperatureChart");

    function handleDragStart(clientX) {
      isDragging = true;
      startX = clientX;
      chartContainer.style.cursor = "grabbing";
    }

    function handleDragMove(clientX) {
      if (!isDragging) return;
      const deltaX = clientX - startX;
      if (Math.abs(deltaX) > dragSensitivity) {
        const newIndex = currentIndex + (deltaX > 0 ? -1 : 1);
        if (newIndex >= 0 && newIndex + daysToShow <= weatherData.length) {
          currentIndex = newIndex;
          startX = clientX;
          updateChart();
        }
      }
    }

    function handleDragEnd() {
      isDragging = false;
      chartContainer.style.cursor = "grab";
    }

    // Sự kiện chuột
    canvas.addEventListener("mousedown", (e) => {
      e.preventDefault();
      handleDragStart(e.clientX);
    });

    window.addEventListener("mousemove", (e) => {
      e.preventDefault();
      handleDragMove(e.clientX);
    });

    window.addEventListener("mouseup", () => {
      handleDragEnd();
    });

    // Sự kiện cảm ứng
    canvas.addEventListener("touchstart", (e) => {
      e.preventDefault();
      handleDragStart(e.touches[0].clientX);
    });

    window.addEventListener("touchmove", (e) => {
      e.preventDefault();
      handleDragMove(e.touches[0].clientX);
    });

    window.addEventListener("touchend", () => {
      handleDragEnd();
    });
  } catch (error) {
    console.error("Lỗi khi tải dữ liệu:", error);
    alert("Không thể tải dữ liệu thời tiết. Vui lòng thử lại sau.");
  }
}

function updateChart() {
  // Lấy dữ liệu cho 5 ngày
  const start = currentIndex;
  const end = Math.min(currentIndex + daysToShow, weatherData.length);
  const slicedData = weatherData.slice(start, end);

  // Chuẩn bị dữ liệu cho biểu đồ
  const labels = slicedData.map((data) => formatDate(data.date));
  const highTemps = slicedData.map((data) => data.highTemperature);
  const lowTemps = slicedData.map((data) => data.lowTemperature);

  // Tạo biểu đồ mới
  const ctx = document.getElementById("temperatureChart").getContext("2d");

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Nhiệt độ cao (°C)",
          data: highTemps,
          borderColor: "#FF6B6B",
          backgroundColor: "#FF6B6B",
          fill: false,
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 10,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: "#FF6B6B",
          pointBorderWidth: 3,
          datalabels: {
            align: "top",
            formatter: (value) => `${value.toFixed(1)}°`,
            color: "#FF6B6B",
            font: {
              size: 24,
              weight: "bold",
              family: "'Helvetica Neue', Arial, sans-serif",
            },
            padding: 8,
          },
        },
        {
          label: "Nhiệt độ thấp (°C)",
          data: lowTemps,
          borderColor: "#4ECDC4",
          backgroundColor: "#4ECDC4",
          fill: false,
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 10,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: "#4ECDC4",
          pointBorderWidth: 3,
          datalabels: {
            align: "bottom",
            formatter: (value) => `${value.toFixed(1)}°`,
            color: "#4ECDC4",
            font: {
              size: 24,
              weight: "bold",
              family: "'Helvetica Neue', Arial, sans-serif",
            },
            padding: 8,
          },
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 30,
          right: 20,
          bottom: 30,
          left: 20,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: Math.min(...lowTemps) - 5,
          max: Math.max(...highTemps) + 5,
          grid: {
            color: "rgba(200, 200, 200, 0.2)",
            drawBorder: false,
          },
          ticks: {
            font: {
              size: 25,
              weight: "500",
              family: "'Helvetica Neue', Arial, sans-serif",
            },
            padding: 20,
            callback: function (value) {
              return value.toFixed(1) + "°C";
            },
            color: "#666666",
          },
        },
        x: {
          grid: {
            display: false,
          },
          ticks: {
            font: {
              size: 20,
              weight: "500",
              family: "'Helvetica Neue', Arial, sans-serif",
            },
            padding: 80,
            maxRotation: 0,
            minRotation: 0,
            callback: function (value, index) {
              const data = slicedData[index];
              return [
                formatDate(data.date),
                "",
                getWeatherIcon(data.weather),
                "",
                `${data.windSpeed} km/h`,
                "",
                getWindDirectionArrow(data.windDirection),
                "",
                `${data.chance_rain}%`,
              ];
            },
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          align: "center",
          labels: {
            font: {
              size: 16,
              weight: "bold",
              family: "'Helvetica Neue', Arial, sans-serif",
            },
            usePointStyle: true,
            padding: 20,
            color: "#333333",
          },
        },
        tooltip: {
          enabled: true,
          mode: "index",
          intersect: false,
          padding: 12,
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          titleColor: "#333333",
          bodyColor: "#666666",
          borderColor: "rgba(0, 0, 0, 0.1)",
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              if (label) {
                label += ": ";
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(1) + "°C";
              }
              return label;
            },
          },
        },
        datalabels: {
          display: true,
        },
      },
    },
    plugins: [ChartDataLabels],
  });
}

function updateWeatherDetails() {
  // Lấy các phần tử hiển thị
  const dayLabels = document.querySelectorAll("#dayLabels div");
  const weatherIcons = document.querySelectorAll(".weather-icons div");
  const windSpeeds = document.querySelectorAll(".wind-speed");
  const windDirections = document.querySelectorAll(".wind-direction");
  const precipitationValues = document.querySelectorAll(".precipitation-value");
  const chanceRainValues = document.querySelectorAll(".chance-rain-value");

  // Lấy dữ liệu thời tiết cho 5 ngày hiển thị
  const displayData = weatherData.slice(currentIndex, currentIndex + 5);

  // Cập nhật từng phần tử
  displayData.forEach((data, index) => {
    // Cập nhật ngày
    const date = new Date(data.date);
    const dayOfWeek = date.toLocaleDateString("vi-VN", { weekday: "short" });
    dayLabels[index].textContent = dayOfWeek;

    // Cập nhật biểu tượng thời tiết
    weatherIcons[index].textContent = getWeatherIcon(data.weather);

    // Cập nhật tốc độ gió
    windSpeeds[index].textContent = data.windSpeed;

    // Cập nhật hướng gió và xoay mũi tên
    const arrowRotation = getWindDirectionRotation(data.windDirection);
    windDirections[index].style.transform = `rotate(${arrowRotation}deg)`;

    // Cập nhật lượng mưa
    precipitationValues[index].textContent = data.precipitation;

    // Cập nhật khả năng mưa
    chanceRainValues[index].textContent = data.chance_rain;
  });
}

// Khởi tạo
document.addEventListener("DOMContentLoaded", function () {
  // Thêm sự kiện cho menu chọn khu vực
  document
    .getElementById("locationSelect")
    .addEventListener("change", handleLocationChange);

  // Tải dữ liệu ban đầu
  loadWeatherData();
});

// Dữ liệu mẫu cho Đồng Nai
const sampleWeatherData = {
  location: "Đồng Nai",
  current: {
    temperature: 32,
    weather: "rain",
    chanceOfRain: 50,
    humidity: 74,
    windSpeed: 11,
    feelsLike: 36
  },
  hourly: [
    { time: "12:00", temperature: 32, weather: "rain", windSpeed: 10, windDirection: "↑", precipitation: 40 },
    { time: "15:00", temperature: 31, weather: "rain", windSpeed: 10, windDirection: "↑", precipitation: 50 },
    { time: "18:00", temperature: 31, weather: "thunderstorm", windSpeed: 6, windDirection: "↑", precipitation: 25 },
    { time: "21:00", temperature: 28, weather: "rain", windSpeed: 6, windDirection: "↑", precipitation: 10 },
    { time: "00:00", temperature: 27, weather: "thunderstorm", windSpeed: 5, windDirection: "↑", precipitation: 10 },
    { time: "03:00", temperature: 26, weather: "thunderstorm", windSpeed: 5, windDirection: "←", precipitation: 10 },
    { time: "06:00", temperature: 26, weather: "thunderstorm", windSpeed: 5, windDirection: "←", precipitation: 10 },
    { time: "09:00", temperature: 29, weather: "thunderstorm", windSpeed: 5, windDirection: "↑", precipitation: 10 }
  ],
  daily: [
    { day: "CN", weather: "rain", highTemp: 32, lowTemp: 26 },
    { day: "Th 2", weather: "rain", highTemp: 33, lowTemp: 27 },
    { day: "Th 3", weather: "thunderstorm", highTemp: 34, lowTemp: 27 },
    { day: "Th 4", weather: "rain", highTemp: 34, lowTemp: 26 },
    { day: "Th 5", weather: "thunderstorm", highTemp: 33, lowTemp: 27 },
    { day: "Th 6", weather: "thunderstorm", highTemp: 33, lowTemp: 26 },
    { day: "Th 7", weather: "thunderstorm", highTemp: 30, lowTemp: 26 },
    { day: "CN", weather: "thunderstorm", highTemp: 32, lowTemp: 26 }
  ]
};

// Hàm lấy biểu tượng thời tiết
function getWeatherIcon(weather) {
  const icons = {
    sunny: "☀️",
    rain: "🌧️",
    cloudy: "☁️",
    "partly cloudy": "⛅",
    thunderstorm: "⛈️",
    snow: "❄️",
    mist: "🌫️",
  };
  return icons[weather.toLowerCase()] || "⛅";
}

// Function to set up the tabs
function setupTabs() {
  const tabs = document.querySelectorAll('.tab');
  const charts = document.querySelectorAll('.chart');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs and charts
      tabs.forEach(t => t.classList.remove('active'));
      charts.forEach(c => c.classList.remove('active'));

      // Add active class to clicked tab and corresponding chart
      tab.classList.add('active');
      const tabName = tab.getAttribute('data-tab');
      document.getElementById(`${tabName}Chart`).classList.add('active');

      // If switching to wind tab, initialize the wind arrows
      if (tabName === 'wind') {
        updateWindArrows();
      }

      // If switching to temperature tab, update temperature dots
      if (tabName === 'temperature') {
        updateTemperatureDots();
      }
    });
  });
}

// Function to update wind arrows based on the data-direction attribute
function updateWindArrows() {
  const windValues = document.querySelectorAll('.wind-value');

  windValues.forEach(windValue => {
    const direction = windValue.getAttribute('data-direction');
    const arrow = windValue.querySelector('.wind-arrow');

    if (arrow && direction) {
      // Make sure the arrow rotation is set correctly
      switch (direction) {
        case 'N':
          arrow.style.transform = 'rotate(0deg)';
          break;
        case 'NE':
          arrow.style.transform = 'rotate(45deg)';
          break;
        case 'E':
          arrow.style.transform = 'rotate(90deg)';
          break;
        case 'SE':
          arrow.style.transform = 'rotate(135deg)';
          break;
        case 'S':
          arrow.style.transform = 'rotate(180deg)';
          break;
        case 'SW':
          arrow.style.transform = 'rotate(225deg)';
          break;
        case 'W':
          arrow.style.transform = 'rotate(270deg)';
          break;
        case 'NW':
          arrow.style.transform = 'rotate(315deg)';
          break;
      }
    }
  });
}

// Function to update temperature dots and animations
function updateTemperatureDots() {
  // Get temperature values and SVG elements
  const tempValues = document.querySelectorAll('.temp-value');
  const tempNumbers = Array.from(document.querySelectorAll('.temp-number')).map(el => parseInt(el.textContent, 10));
  const maxTemp = Math.max(...tempNumbers);
  const minTemp = Math.min(...tempNumbers);
  const range = maxTemp - minTemp;

  if (range > 0) {
    // Get SVG path elements
    const pathElement = document.querySelector('.temperature-path');
    const areaElement = document.querySelector('.temperature-area');
    const svgElement = document.querySelector('.temperature-svg');

    // Get dimensions
    const chartContainer = document.getElementById('temperatureChart');
    const svgWidth = chartContainer.clientWidth;
    const svgHeight = chartContainer.clientHeight - 30; // Subtract time marker height

    // Calculate points for the path - normalize to percentage of width/height
    const points = tempNumbers.map((temp, index) => {
      // Calculate x position - evenly distributed along width
      const x = 15 + (index / (tempNumbers.length - 1)) * (svgWidth - 30); // 15px padding on each side

      // Calculate y position - map temperature to the SVG height (inverted)
      // Higher temperature = higher on chart (lower y value)
      const normalizedTemp = (temp - minTemp) / range;
      // Use 70% of the height to leave room for the time markers at bottom
      const y = svgHeight * 0.7 * (1 - normalizedTemp) + svgHeight * 0.1;

      return { x, y };
    });

    // Create a path string for SVG
    // Start with a move to the first point
    let pathD = `M ${points[0].x},${points[0].y}`;

    // For each subsequent point, add a cubic bezier curve
    for (let i = 0; i < points.length - 1; i++) {
      const current = points[i];
      const next = points[i + 1];

      // Calculate control points for a smooth curve
      const controlX1 = current.x + (next.x - current.x) / 3;
      const controlY1 = current.y;
      const controlX2 = next.x - (next.x - current.x) / 3;
      const controlY2 = next.y;

      // Add the curve segment to the path
      pathD += ` C ${controlX1},${controlY1} ${controlX2},${controlY2} ${next.x},${next.y}`;
    }

    // Set the path attribute
    if (pathElement) {
      pathElement.setAttribute('d', pathD);
    }

    // Create the area path by extending the line path down to the bottom
    if (areaElement) {
      const areaPath = pathD +
        ` L ${points[points.length - 1].x},${svgHeight} L ${points[0].x},${svgHeight} Z`;
      areaElement.setAttribute('d', areaPath);
    }

    // Position the temperature dots directly on the curve
    tempValues.forEach((tempValue, index) => {
      const point = points[index];

      // Set absolute position for each temperature value
      tempValue.style.left = `${point.x}px`;
      tempValue.style.top = `${point.y}px`;

      // Add animation effect to dots
      const dot = tempValue.querySelector('.temp-dot');
      if (dot) {
        setTimeout(() => {
          dot.style.transform = 'scale(1.2)';
          setTimeout(() => {
            dot.style.transform = 'scale(1)';
          }, 200);
        }, index * 100);
      }
    });
  }
}

// Make sure to call updateTemperatureDots when window resizes
window.addEventListener('resize', function () {
  // Only update if the temperature chart is active
  if (document.getElementById('temperatureChart').classList.contains('active')) {
    updateTemperatureDots();
  }
});

// Thêm hiệu ứng hover cho forecast items
function setupForecastItemsInteraction() {
  const forecastItems = document.querySelectorAll('.forecast-item');

  forecastItems.forEach(item => {
    item.addEventListener('click', () => {
      // Reset active state
      forecastItems.forEach(fi => fi.classList.remove('today'));
      // Set active state
      item.classList.add('today');

      // Hiển thị thông báo khi người dùng click vào ngày
      const dayName = item.querySelector('.day-name').textContent;
      const highTemp = item.querySelector('.high').textContent;

      // Tạo hiệu ứng ripple khi click
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      item.appendChild(ripple);

      const rect = item.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);

      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${0}px`;
      ripple.style.top = `${0}px`;

      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
}

// Thêm hiệu ứng chuyển đổi đơn vị nhiệt độ
function setupTemperatureUnitToggle() {
  const degreeElement = document.querySelector('.degree');
  let isCelsius = true;

  degreeElement.addEventListener('click', () => {
    const tempElement = document.querySelector('.temperature');
    const currentTemp = parseInt(tempElement.textContent);
    let newTemp;

    if (isCelsius) {
      // Chuyển từ C sang F
      newTemp = Math.round((currentTemp * 9 / 5) + 32);
      degreeElement.textContent = '°F|°C';
    } else {
      // Chuyển từ F sang C
      newTemp = Math.round((currentTemp - 32) * 5 / 9);
      degreeElement.textContent = '°C|°F';
    }

    // Tạo hiệu ứng đếm số
    const countUp = setInterval(() => {
      const currentDisplayTemp = parseInt(tempElement.textContent);

      if (isCelsius) {
        // Tăng dần nếu đang chuyển từ C -> F
        if (currentDisplayTemp < newTemp) {
          tempElement.textContent = (currentDisplayTemp + 1).toString();
        } else {
          clearInterval(countUp);
        }
      } else {
        // Giảm dần nếu đang chuyển từ F -> C
        if (currentDisplayTemp > newTemp) {
          tempElement.textContent = (currentDisplayTemp - 1).toString();
        } else {
          clearInterval(countUp);
        }
      }
    }, 50);

    isCelsius = !isCelsius;
  });
}

// Initialize the application
function init() {
  // Set up tabs
  setupTabs();

  // Initialize wind arrows
  updateWindArrows();

  // Initialize temperature dots
  updateTemperatureDots();

  // Thiết lập hiệu ứng cho forecast items
  setupForecastItemsInteraction();

  // Thiết lập chuyển đổi đơn vị nhiệt độ
  setupTemperatureUnitToggle();

  // Hiển thị biểu tượng thời tiết cho prognosis
  document.querySelectorAll('.forecast-item .weather-icon').forEach(icon => {
    if (icon.textContent === '🌧️' || icon.textContent === '⛈️') {
      // Giữ nguyên icon đã có
    } else {
      // Nếu chưa có, set từ dữ liệu
      const parentElement = icon.closest('.forecast-item');
      if (parentElement) {
        const dayName = parentElement.querySelector('.day-name').textContent;
        const dayData = sampleWeatherData.daily.find(d => d.day === dayName);
        if (dayData) {
          icon.textContent = getWeatherIcon(dayData.weather);
        }
      }
    }
  });

  // Xử lý sự kiện khi click vào location selector
  document.querySelector('.location-selector').addEventListener('click', () => {
    // Tạo dropdown menu
    const existingDropdown = document.querySelector('.location-dropdown');

    if (existingDropdown) {
      existingDropdown.remove();
      return;
    }

    const dropdown = document.createElement('div');
    dropdown.className = 'location-dropdown';

    const locations = [
      'Đồng Nai', 'TP Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Huế', 'Cần Thơ'
    ];

    locations.forEach(loc => {
      const item = document.createElement('div');
      item.className = 'dropdown-item';
      item.textContent = loc;

      if (loc === 'Đồng Nai') {
        item.classList.add('active');
      }

      item.addEventListener('click', () => {
        document.querySelector('.location-name').textContent = loc;
        dropdown.remove();
      });

      dropdown.appendChild(item);
    });

    document.querySelector('.location-info').appendChild(dropdown);
  });
}

// Thêm ripple effect CSS vào document
function addRippleEffectStyle() {
  const style = document.createElement('style');
  style.textContent = `
    .ripple {
      position: absolute;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
    }
    
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
    
    .location-dropdown {
      position: absolute;
      top: 100%;
      left: 100px;
      background-color: #303134;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
      z-index: 100;
      overflow: hidden;
      min-width: 180px;
      animation: fadeIn 0.2s ease;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .dropdown-item {
      padding: 12px 16px;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }
    
    .dropdown-item:hover {
      background-color: rgba(138, 180, 248, 0.1);
    }
    
    .dropdown-item.active {
      background-color: rgba(138, 180, 248, 0.2);
      color: #8ab4f8;
    }
  `;
  document.head.appendChild(style);
}

// Chạy sau khi trang đã tải
document.addEventListener('DOMContentLoaded', () => {
  init();
  addRippleEffectStyle();
});
