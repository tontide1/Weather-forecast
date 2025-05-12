# #!/bin/bash

# # Exit on any error
# set -e

# echo "=== CHECK PYTHON VERSION ==="
# if ! python --version 2>&1 | grep -q "Python 3"; then
#     echo "ERROR: Python3 is required!"
#     exit 1
# fi
# echo "=== PYTHON VERSION CHECKED ==="

# # No need to load .env file manually as Docker Compose does this for us
# # when using env_file directive
# echo "=== CHECKING ENVIRONMENT VARIABLES ==="
# required_vars=("DATABASE_NAME" "DATABASE_USER" "DATABASE_PASSWORD" "DATABASE_HOST" "DATABASE_PORT")
# for var in "${required_vars[@]}"; do
#     if [ -z "${!var}" ]; then
#         echo "ERROR: Required environment variable $var is not set!"
#         exit 1
#     fi
# done
# echo "=== ENVIRONMENT VARIABLES CHECKED ==="


# echo "=== WAIT FOR DATABASE ==="
# until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER; do
#     echo "Database is not ready yet, waiting..."
#     sleep 2
# done
# echo "=== DATABASE IS AVAILABLE ==="

# echo "=== CONNECT TO DATABASE ==="
# export PGPASSWORD="$DATABASE_PASSWORD"
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "SELECT 1;" >/dev/null 2>&1
# if [ $? -ne 0 ]; then
#     echo "ERROR: Cannot connect to PostgreSQL!"
#     echo "Check PostgreSQL server and sign-in information!"
#     exit 1
# fi
# echo "=== DATABASE IS READY ==="

# echo "=== CREATE DATABASE ==="
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "DROP DATABASE IF EXISTS $DATABASE_NAME;"
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "CREATE DATABASE $DATABASE_NAME WITH ENCODING='UTF8' TEMPLATE=template0;"
# echo "=== CREATE DATABASE COMPLETELY ==="

# echo "=== UPDATE METADATA OF DATABASE ==="
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "ALTER DATABASE $DATABASE_NAME REFRESH COLLATION VERSION;"
# echo "=== UPDATE METADATA OF DATABASE COMPLETELY ==="

# echo "=== CREATE VIRTUAL ENVIRONMENT ==="
# python -m venv venv || { echo "❌ Failed to create venv"; exit 1; }
# if [ -f "venv/bin/activate" ]; then
#     source venv/bin/activate
#     if [ -f "requirements.txt" ]; then
#         pip install --upgrade pip
#         pip install wheel setuptools
#         echo "📦 Installing dependencies from requirements.txt..."
#         pip install --upgrade pip
#         pip install -r requirements.txt || { echo "❌ Failed to install requirements."; exit 1; }
#     else
#         echo "⚠️  requirements.txt not found. Skipping dependency installation."
#     fi
# else
#     echo "❌ Activate script not found! venv creation may have failed."
#     exit 1
# fi
# echo "=== VIRTUAL ENVIRONMENT ACTIVATED ==="

# if [ ! -d src ]; then
#     echo "ERROR: src directory not found!"
#     exit 1
# fi

# echo "=== CREATE DATABASE TABLE ==="
# python src_data/insert.py
# echo "=== CREATE DATABASE TABLE COMPLETELY ==="

# echo "=== NAVIGATE TO PROJECT DIRECTORY ==="
# cd /app/src

# echo "=== CREATE STATIC & MEDIA DIRECTORIES IF NOT EXIST ==="
# mkdir -p static media

# echo "=== COLLECT STATIC FILES ==="
# python manage.py collectstatic --noinput

# # echo "=== LIST STATICFILES ==="
# # ls -R /app/src/staticfiles/web_app

# echo "=== CREATE MIGRATIONS ==="
# find /app/src/*/migrations/ -type f -name "*.py" ! -name "__init__.py" -exec rm -f {} +
# python manage.py makemigrations
# if [ $? -ne 0 ]; then
#     echo "ERROR: Cannot create migrations"
#     exit 1
# fi
# python manage.py migrate
# if [ $? -ne 0 ]; then
#     echo "ERROR: Cannot apply migrations"
#     echo "Check PostgreSQL connection"
#     exit 1
# fi
# echo "=== CREATE MIGRATIONS COMPLETELY ==="

# echo "=== CREATE ADMIN ACCOUNT ==="
# # Check if admin credentials are set
# if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
#     python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD') if not User.objects.filter(username='$ADMIN_USERNAME').exists() else print('Admin already exists!')"
#     echo "Admin account created or already exists"
# else
#     echo "Skipping admin creation - credentials not fully provided"
# fi
# echo "=== CREATE ADMIN ACCOUNT PROCESS COMPLETED ==="

# echo "=== RUN SERVER ==="
# exec "$@"
#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "=== CHECK PYTHON VERSION ==="
if ! python --version 2>&1 | grep -q "Python 3"; then
    echo "ERROR: Python3 is required!"
    exit 1
fi
echo "=== PYTHON VERSION CHECKED ==="

# Check if required environment variables are set
# These should be passed by Docker Compose from .env file or its own environment block
echo "=== CHECKING ENVIRONMENT VARIABLES ==="
required_vars=("DATABASE_NAME" "DATABASE_USER" "DATABASE_PASSWORD" "DATABASE_HOST" "DATABASE_PORT")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then # Check if the variable is empty or unset
        echo "ERROR: Required environment variable $var is not set!"
        echo "Please ensure it is defined in your .env file and referenced in docker-compose.yml"
        exit 1
    fi
done
echo "=== ENVIRONMENT VARIABLES CHECKED (values are set) ==="
# You can optionally print them for debugging, but be careful with passwords in logs
# echo "DATABASE_HOST: $DATABASE_HOST"
# echo "DATABASE_PORT: $DATABASE_PORT"
# echo "DATABASE_USER: $DATABASE_USER"
# echo "DATABASE_NAME: $DATABASE_NAME"
# (Avoid printing DATABASE_PASSWORD)

echo "=== WAIT FOR DATABASE ($DATABASE_HOST:$DATABASE_PORT) ==="
# Loop until pg_isready successfully connects as the specified user
# The -d flag can be used to specify the database name for a more specific check if needed,
# but for just availability, -U is usually sufficient.
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -q; do
    echo "Database is not ready yet (user: $DATABASE_USER, host: $DATABASE_HOST, port: $DATABASE_PORT), waiting..."
    sleep 2
done
echo "=== DATABASE IS AVAILABLE ==="

echo "=== VERIFYING DATABASE CONNECTION WITH PGPASSWORD ==="
export PGPASSWORD="$DATABASE_PASSWORD"
# Attempt a simple query. If this fails, it means the password might be wrong,
# or the database/user setup by Postgres entrypoint didn't complete as expected.
if ! psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "---------------------------------------------------------------------"
    echo "ERROR: Failed to connect to database '$DATABASE_NAME' as user '$DATABASE_USER' on $DATABASE_HOST:$DATABASE_PORT."
    echo "This usually means:"
    echo "1. The PostgreSQL container (service 'db') hasn't finished initializing the database with POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB."
    echo "2. The DATABASE_PASSWORD used by this 'web' service does not match the password set for '$DATABASE_USER' in PostgreSQL."
    echo "3. The database '$DATABASE_NAME' does not exist (PostgreSQL should create it if POSTGRES_DB was set)."
    echo "Troubleshooting steps:"
    echo " - Ensure DATABASE_PASSWORD in your .env file is correct and matches what PostgreSQL used for initialization."
    echo " - Check logs of the 'db' service for errors during its startup and database creation."
    echo " - If you recently changed passwords, you might need to remove the PostgreSQL data volume and let it re-initialize."
    echo "---------------------------------------------------------------------"
    exit 1
fi
echo "=== DATABASE CONNECTION VERIFIED AND READY ==="

# === IMPORTANT: DATABASE CREATION AND MIGRATION STRATEGY ===
# The PostgreSQL service ('db') is responsible for creating the initial database
# based on POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD environment variables
# when its data volume is first initialized.
#
# DO NOT automatically DROP/CREATE DATABASE here in the web's entrypoint for production
# or if you want to persist data.
# This script will now assume the database an_user already exist.

# echo "=== (SKIPPED) CREATE DATABASE (SHOULD BE HANDLED BY POSTGRES SERVICE) ==="
# The following lines are commented out as they are destructive and usually not desired
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "DROP DATABASE IF EXISTS $DATABASE_NAME;"
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "CREATE DATABASE $DATABASE_NAME WITH ENCODING='UTF8' TEMPLATE=template0;"
# echo "=== (SKIPPED) CREATE DATABASE COMPLETELY ==="

# echo "=== (SKIPPED) UPDATE METADATA OF DATABASE (RARELY NEEDED) ==="
# psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -c "ALTER DATABASE $DATABASE_NAME REFRESH COLLATION VERSION;"
# echo "=== (SKIPPED) UPDATE METADATA OF DATABASE COMPLETELY ==="


# === VIRTUAL ENVIRONMENT AND DEPENDENCIES ===
# Using a virtual environment inside Docker is often redundant as the container itself is an isolated environment.
# Dependencies are typically installed globally within the container during the Docker image build process (in Dockerfile).
# If you choose to keep it, ensure 'venv' directory is part of your .dockerignore or managed appropriately.
echo "=== (CONSIDER REMOVING) CREATE VIRTUAL ENVIRONMENT ==="
python -m venv venv || { echo "❌ Failed to create venv"; exit 1; }
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    if [ -f "requirements.txt" ]; then
        echo "🐍 Upgrading pip, installing wheel and setuptools..."
        pip install --upgrade pip wheel setuptools
        echo "📦 Installing dependencies from requirements.txt..."
        pip install -r requirements.txt || { echo "❌ Failed to install requirements."; exit 1; }
    else
        echo "⚠️  requirements.txt not found. Skipping dependency installation."
    fi
else
    echo "❌ Activate script not found! venv creation may have failed."
    exit 1
fi
echo "=== VIRTUAL ENVIRONMENT ACTIVATED (CONSIDER REMOVING THIS STEP) ==="


if [ ! -d "src" ]; then # Assuming WORKDIR is /app, so src is at /app/src
    echo "ERROR: src directory not found at /app/src!"
    exit 1
fi

# It's generally better to run scripts like insert.py as Django management commands
# after migrations, if they depend on the Django ORM.
# For now, assuming it's a standalone script or handles its own DB connection.
echo "=== (REVIEW) CREATE DATABASE TABLE (running src_data/insert.py) ==="
if [ -f "src_data/insert.py" ]; then
    python src_data/insert.py
    echo "=== CREATE DATABASE TABLE COMPLETELY ==="
else
    echo "⚠️  src_data/insert.py not found. Skipping."
fi


echo "=== NAVIGATE TO PROJECT DIRECTORY (/app/src) ==="
cd /app/src # Ensure this path is correct relative to your WORKDIR

echo "=== CREATE STATIC & MEDIA DIRECTORIES IF NOT EXIST ==="
mkdir -p staticfiles media # Changed 'static' to 'staticfiles' to match Django convention for collectstatic output

echo "=== COLLECT STATIC FILES ==="
python manage.py collectstatic --noinput --clear # --clear is useful to remove old files

# === MIGRATIONS STRATEGY ===
# Deleting old migration files automatically is DANGEROUS and breaks Django's migration system.
# Migrations should be managed as part of your development workflow, not reset on every startup.
# echo "=== (REMOVED DESTRUCTIVE MIGRATION CLEANUP) ==="
# find /app/src/*/migrations/ -type f -name "*.py" ! -name "__init__.py" -exec rm -f {} +

echo "=== APPLYING DATABASE MIGRATIONS ==="
# makemigrations should typically be run during development, not automatically on startup,
# unless your workflow specifically requires it.
# Consider only running migrate on startup.
python manage.py makemigrations # Be cautious with running this automatically
if [ $? -ne 0 ]; then
    echo "WARNING: 'makemigrations' encountered issues. This is often okay if no model changes were made."
    # exit 1 # You might not want to exit here, as it could be a non-critical warning
fi
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot apply migrations ('migrate' command failed)!"
    echo "Check database connection, previous migration states, and model definitions."
    exit 1
fi
echo "=== DATABASE MIGRATIONS APPLIED SUCCESSFULLY ==="

echo "=== CREATE ADMIN ACCOUNT (if credentials provided and user doesn't exist) ==="
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
    # Ensure this manage.py command can run without error if the user already exists.
    # The command provided already handles this with 'if not User.objects.filter(...).exists()'
    echo "Attempting to create/ensure admin user: $ADMIN_USERNAME"
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD') if not User.objects.filter(username='$ADMIN_USERNAME').exists() else print('Admin user $ADMIN_USERNAME already exists.')"
    echo "Admin account process completed."
else
    echo "Skipping admin user creation - ADMIN_USERNAME, ADMIN_EMAIL, or ADMIN_PASSWORD not fully provided."
fi
echo "=== ADMIN ACCOUNT SETUP COMPLETED ==="

echo "=== RUN SERVER (executing command: $@) ==="
exec "$@"