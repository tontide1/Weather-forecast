#!/bin/bash

# ========================================
# Weather Forecast Docker Management Script (Bash)
# ========================================

# Exit on any error
set -e

# --- Configuration ---
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
PROJECT_NAME="weather-forecast" # Used for volume names, derived from directory usually

# --- Colors ---
COLOR_RESET=$(tput sgr0)
COLOR_INFO=$(tput setaf 6)    # Cyan
COLOR_SUCCESS=$(tput setaf 2) # Green
COLOR_WARNING=$(tput setaf 3) # Yellow
COLOR_ERROR=$(tput setaf 1)   # Red
COLOR_HIGHLIGHT=$(tput setaf 5) # Magenta

# --- Default Argument Values ---
ACTION="help"
DETACHED_MODE="true"
BUILD_NO_CACHE="false"
PRUNE_DANGLING="false"

# --- Helper Functions ---
print_info() { echo -e "${COLOR_INFO}$1${COLOR_RESET}"; }
print_success() { echo -e "${COLOR_SUCCESS}$1${COLOR_RESET}"; }
print_warning() { echo -e "${COLOR_WARNING}$1${COLOR_RESET}"; }
print_error() { echo -e "${COLOR_ERROR}$1${COLOR_RESET}"; }
print_highlight() { echo -e "${COLOR_HIGHLIGHT}$1${COLOR_RESET}"; }

test_docker() {
    if docker info >/dev/null 2>&1; then
        return 0
    else
        print_error "Docker is not running or not installed!"
        print_error "Please start Docker Desktop or install Docker before running this script."
        return 1
    fi
}

test_docker_compose() {
    if docker compose version >/dev/null 2>&1; then
        return 0
    else
        print_error "Docker Compose v2 is not available!"
        print_error "Please make sure Docker Compose v2 (docker compose) is installed and accessible."
        return 1
    fi
}

show_help() {
    print_highlight "Weather Forecast Docker Management Script"
    print_highlight "========================================="
    echo ""
    print_info "Usage: $0 [action] [options]"
    echo ""
    print_highlight "Actions:"
    print_info "  start          : Start the containers (default: detached mode)"
    print_info "  stop           : Stop and remove the containers"
    print_info "  restart        : Restart the containers"
    print_info "  logs           : Show container logs (follow)"
    print_info "  status         : Show container status"
    print_info "  build          : Build container images"
    print_info "  clean          : Stop containers and clean up resources"
    print_info "  help           : Show this help information"
    echo ""
    print_highlight "Options:"
    print_info "  --attached     : Run 'start' in attached mode (overrides default detached)"
    print_info "  --no-cache     : Use with 'start' or 'build' to build without cache"
    print_info "  --prune        : Use with 'clean' to remove dangling images and project volumes"
    echo ""
    print_highlight "Examples:"
    print_info "  $0 start"
    print_info "  $0 start --no-cache"
    print_info "  $0 start --attached"
    print_info "  $0 logs"
    print_info "  $0 clean --prune"
}

# --- Docker Operations ---
start_weather_forecast() {
    if [[ ! -f "$PROJECT_DIR/$ENV_FILE" ]]; then
        print_warning "Warning: $ENV_FILE file not found in $PROJECT_DIR!"
        print_warning "Make sure all required environment variables are set in Docker Compose or the environment."
    fi

    detach_flag="-d"
    if [[ "$DETACHED_MODE" == "false" ]]; then
        detach_flag=""
    fi

    build_cmd_flag=""
    if [[ "$BUILD_NO_CACHE" == "true" ]]; then
        build_cmd_flag="--build --no-cache"
    fi
    
    print_info "Starting Weather Forecast services..."
    local cmd="docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" up $detach_flag $build_cmd_flag"
    print_highlight "Running: $cmd"
    eval "$cmd" # Use eval to handle flags correctly if they are empty
    
    if [[ $? -eq 0 && "$DETACHED_MODE" == "true" ]]; then
        echo # Newline for better readability
        print_success "Services started successfully in detached mode!"
        print_info "- To view logs: $0 logs"
        print_info "- To stop services: $0 stop"
        print_info "- To check status: $0 status"
        echo # Newline
        print_success "Application should be available at: http://localhost:8000"
    elif [[ $? -ne 0 ]]; then
        print_error "Failed to start services."
    fi
}

stop_weather_forecast() {
    print_info "Stopping Weather Forecast services..."
    docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" down
    
    if [[ $? -eq 0 ]]; then
        print_success "Services stopped successfully!"
    else
        print_error "Failed to stop services."
    fi
}

restart_weather_forecast() {
    print_info "Restarting Weather Forecast services..."
    stop_weather_forecast
    start_weather_forecast # This will re-evaluate DETACHED_MODE and BUILD_NO_CACHE
}

show_logs() {
    print_info "Showing logs (press Ctrl+C to exit)..."
    docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" logs -f
}

show_status() {
    print_info "Status of Weather Forecast services:"
    docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" ps
}

build_images() {
    local no_cache_flag=""
    if [[ "$BUILD_NO_CACHE" == "true" ]]; then
        no_cache_flag="--no-cache"
    fi
    print_info "Building Docker images for Weather Forecast..."
    docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" build $no_cache_flag
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker images built successfully!"
    else
        print_error "Failed to build images."
    fi
}

clean_environment() {
    print_info "Cleaning up Weather Forecast Docker environment..."
    
    print_info "Stopping and removing containers..."
    docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" down
    
    if [[ "$PRUNE_DANGLING" == "true" ]]; then
        print_warning "Removing dangling images..."
        docker image prune -f
        
        print_warning "Removing project volumes (${PROJECT_NAME}_postgres_data, ${PROJECT_NAME}_static_volume, ${PROJECT_NAME}_media_volume)..."
        # Docker compose usually names volumes <projectname>_<volumename>
        # The project name is often the directory name.
        docker volume rm "${PROJECT_NAME}_postgres_data" "${PROJECT_NAME}_static_volume" "${PROJECT_NAME}_media_volume" 2>/dev/null || print_warning "Some volumes may not have existed or could not be removed."
    fi
    
    print_success "Clean up completed!"
}

# --- Argument Parsing ---
if [[ $# -gt 0 ]]; then
    ACTION="$1"
    shift # Remove action from arguments
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --attached)
            DETACHED_MODE="false"
            shift
            ;;
        --no-cache)
            BUILD_NO_CACHE="true"
            shift
            ;;
        --prune)
            PRUNE_DANGLING="true"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done


# --- Main script logic ---
if ! test_docker || ! test_docker_compose; then
    exit 1
fi

# Ensure we are in the project directory context for docker compose
cd "$PROJECT_DIR" || { print_error "Failed to change directory to $PROJECT_DIR"; exit 1; }

case "$ACTION" in
    start)
        start_weather_forecast
        ;;
    stop)
        stop_weather_forecast
        ;;
    restart)
        restart_weather_forecast
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_images
        ;;
    clean)
        clean_environment
        ;;
    help|*) # Default to help
        show_help
        ;;
esac

exit 0
