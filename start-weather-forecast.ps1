#!/usr/bin/env pwsh
#Requires -Version 5.0

# ========================================
# Weather Forecast Docker Management Script
# ========================================

param(
    [Parameter()]
    [ValidateSet("start", "start-web", "start-airflow", "stop", "restart", "logs", "logs-web", "logs-airflow", "status", "build", "clean", "help")]
    [string]$Action = "help",
    
    [Parameter()]
    [switch]$DetachedMode = $true,
    
    [Parameter()]
    [switch]$BuildNoCache = $false,
    
    [Parameter()]
    [switch]$PruneDangling = $false
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = $PSScriptRoot
$COMPOSE_FILE = "docker-compose.yml"
$ENV_FILE = ".env"

# Color definitions for terminal output
$ColorInfo = @{ForegroundColor = "Cyan" }
$ColorSuccess = @{ForegroundColor = "Green" }
$ColorWarning = @{ForegroundColor = "Yellow" }
$ColorError = @{ForegroundColor = "Red" }
$ColorHighlight = @{ForegroundColor = "Magenta" }

function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-Host "Docker is not running or not installed!" @ColorError
        Write-Host "Please start Docker Desktop or install Docker before running this script." @ColorError
        return $false
    }
}

function Test-DockerCompose {
    try {
        docker compose version | Out-Null
        return $true
    }
    catch {
        Write-Host "Docker Compose is not available!" @ColorError
        Write-Host "Please make sure Docker Compose is installed." @ColorError
        return $false
    }
}

function Start-WeatherForecast {
    if (-not (Test-Path -Path $ENV_FILE)) {
        Write-Host "Warning: .env file not found!" @ColorWarning
        Write-Host "Make sure all required environment variables are set in Docker Compose." @ColorWarning
    }

    $detachFlag = if ($DetachedMode) { "-d" } else { "" }
    $buildFlag = if ($BuildNoCache) { "--build --no-cache" } else { "" }
    
    Write-Host "Starting Weather Forecast services..." @ColorInfo
    $command = "docker compose -f `"$COMPOSE_FILE`" up $detachFlag $buildFlag"
    Write-Host "Running: $command" @ColorHighlight
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0 -and $DetachedMode) {
        Write-Host "`nServices started successfully in detached mode!" @ColorSuccess
        Write-Host "- To view logs: $($MyInvocation.MyCommand.Name) logs" @ColorInfo
        Write-Host "- To stop services: $($MyInvocation.MyCommand.Name) stop" @ColorInfo
        Write-Host "- To check status: $($MyInvocation.MyCommand.Name) status" @ColorInfo
        Write-Host "`nApplication should be available at: http://localhost:8000" @ColorSuccess
    }
}

function Stop-WeatherForecast {
    Write-Host "Stopping Weather Forecast services..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services stopped successfully!" @ColorSuccess
    }
}

function Restart-WeatherForecast {
    Write-Host "Restarting Weather Forecast services..." @ColorInfo
    Stop-WeatherForecast
    Start-WeatherForecast
}

function Show-Logs {
    Write-Host "Showing logs (press Ctrl+C to exit)..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" logs -f
}

function Show-Status {
    Write-Host "Status of Weather Forecast services:" @ColorInfo
    docker compose -f "$COMPOSE_FILE" ps
}

function Build-Images {
    $noCache = if ($BuildNoCache) { "--no-cache" } else { "" }
    Write-Host "Building Docker images for Weather Forecast..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" build $noCache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker images built successfully!" @ColorSuccess
    }
}

function Start-WebServices {
    $detach = if ($DetachedMode) { "-d" } else { "" }
    $buildFlag = if ($BuildNoCache) { "--build --no-cache" } else { "" }
    
    Write-Host "Starting web and database services..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" up $detach $buildFlag web db
    
    if ($LASTEXITCODE -eq 0 -and $DetachedMode) {
        Write-Host "Web services started successfully in detached mode!" @ColorSuccess
        Write-Host "Application should be available at:" @ColorInfo
        Write-Host "http://localhost:8000" @ColorHighlight
    }
}

function Start-AirflowServices {
    $detach = if ($DetachedMode) { "-d" } else { "" }
    $buildFlag = if ($BuildNoCache) { "--build --no-cache" } else { "" }
    
    Write-Host "Starting Airflow and database services..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" up $detach $buildFlag db airflow-webserver airflow-scheduler airflow-init
    
    if ($LASTEXITCODE -eq 0 -and $DetachedMode) {
        Write-Host "Airflow services started successfully in detached mode!" @ColorSuccess
        Write-Host "Airflow webserver should be available at:" @ColorInfo
        Write-Host "http://localhost:8080" @ColorHighlight
        Write-Host "Login with admin credentials from .env file" @ColorInfo
    }
}

function Get-WebLogs {
    Write-Host "Showing logs for web services..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" logs -f web db
}

function Get-AirflowLogs {
    Write-Host "Showing logs for Airflow services..." @ColorInfo
    docker compose -f "$COMPOSE_FILE" logs -f airflow-webserver airflow-scheduler airflow-init
}

function Remove-Environment {
    Write-Host "Cleaning up Weather Forecast Docker environment..." @ColorInfo
    
    # Stop containers
    docker compose -f "$COMPOSE_FILE" down
    
    if ($PruneDangling) {
        Write-Host "Removing dangling images and volumes..." @ColorInfo
        docker system prune -f
        
        # Remove volumes
        Write-Host "Removing project volumes..." @ColorWarning
        docker volume rm weather-forecast_postgres_data weather-forecast_static_volume weather-forecast_media_volume 2>$null
    }
    
    Write-Host "Clean up completed!" @ColorSuccess
}

function Show-Help {
    Write-Host "Weather Forecast Docker Management Script" @ColorHighlight
    Write-Host "=========================================" @ColorHighlight
    Write-Host ""
    Write-Host "Usage: $($MyInvocation.MyCommand.Name) [action] [options]" @ColorInfo
    Write-Host ""
    Write-Host "Actions:" @ColorHighlight
    Write-Host "  start          : Start all containers (web, db, and airflow)" @ColorInfo
    Write-Host "  start-web      : Start only web and database containers" @ColorInfo
    Write-Host "  start-airflow  : Start only airflow and database containers" @ColorInfo
    Write-Host "  stop           : Stop and remove the containers" @ColorInfo
    Write-Host "  restart        : Restart the containers" @ColorInfo
    Write-Host "  logs           : Show all container logs" @ColorInfo
    Write-Host "  logs-web       : Show only web container logs" @ColorInfo
    Write-Host "  logs-airflow   : Show only airflow container logs" @ColorInfo
    Write-Host "  status         : Show container status" @ColorInfo
    Write-Host "  build          : Build container images" @ColorInfo
    Write-Host "  clean          : Stop containers and clean up resources" @ColorInfo
    Write-Host "  help           : Show this help information" @ColorInfo
    Write-Host ""
    Write-Host "Options:" @ColorHighlight
    Write-Host "  -DetachedMode   : Run in detached mode (default: true)" @ColorInfo
    Write-Host "  -BuildNoCache   : Build without using cache" @ColorInfo
    Write-Host "  -PruneDangling  : Remove unused images and volumes when cleaning" @ColorInfo
    Write-Host ""
    Write-Host "Examples:" @ColorHighlight
    Write-Host "  $($MyInvocation.MyCommand.Name) start" @ColorInfo
    Write-Host "  $($MyInvocation.MyCommand.Name) start -BuildNoCache" @ColorInfo
    Write-Host "  $($MyInvocation.MyCommand.Name) logs" @ColorInfo
    Write-Host "  $($MyInvocation.MyCommand.Name) clean -PruneDangling" @ColorInfo
}

# Main script logic
if (-not (Test-Docker) -or -not (Test-DockerCompose)) {
    exit 1
}

# Change to project directory
Set-Location $PROJECT_DIR

# Execute requested action
switch ($Action) {
    "start" { Start-WeatherForecast }
    "start-web" { Start-WebServices }
    "start-airflow" { Start-AirflowServices }
    "stop" { Stop-WeatherForecast }
    "restart" { Restart-WeatherForecast }
    "logs" { Show-Logs }
    "logs-web" { Get-WebLogs }
    "logs-airflow" { Get-AirflowLogs }
    "status" { Show-Status }
    "build" { Build-Images }
    "clean" { Remove-Environment }
    "help" { Show-Help }
    default { Show-Help }
}
