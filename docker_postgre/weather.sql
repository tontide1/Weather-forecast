CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,

    temp DECIMAL(5,2),
    dwpt DECIMAL(5,2),
    rhum DECIMAL(5,2),
    wpgt DECIMAL(5,2),
    tsun INTEGER,
    wdir INTEGER,
    coco DECIMAL(5,2),
    weather VARCHAR(100)
);

INSERT INTO weather_data (date, location, temp, dwpt, rhum, wpgt, tsun, wdir, coco, weather)
VALUES 
('2025-04-17', 'Hanoi', 31.5, 25.3, 70.0, 35.6, 320, 180, 40.0, 'Sunny'),
('2025-04-17', 'Ho Chi Minh City', 33.2, 27.8, 75.0, 28.4, 280, 200, 30.0, 'Partly Cloudy')