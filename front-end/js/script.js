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
