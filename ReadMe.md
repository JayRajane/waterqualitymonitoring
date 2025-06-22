pip3 install cryptography

How to generate a valid Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

J5Mg-eBLUQwCcRPNHDDJPiqUlfBPr4yWECns0yVU0DY=


docker-compose up airflow-init  # one-time setup
docker-compose up -d

Open Airflow UI at http://localhost:8081, log in with:
Username: admin
Password: admin

git@github.com-skyt:JayRajane/waterqualitymonitoring.git

docker-compose down -v
docker-compose up airflow-init
docker-compose up -d

to exit: docker-compose run --rm airflow-init

# To Start the docker airflow service:
**docker-compose run --rm airflow-init**
This will initialize the Airflow DB and create the admin user.
It runs and exits without affecting other containers.

**docker-compose up -d airflow-webserver airflow-scheduler airflow-worker redis**
This starts only Airflow and Redis, and keeps your existing web (Django) and mysql services running.

**docker ps -a**

NOTE: If any new modules or plugin added then restart the docker services
**docker-compose restart airflow-webserver airflow-scheduler airflow-worker**

If DB schema is changed:
**docker-compose run --rm airflow-init**

To take any specific service up
**docker-compose up -d airflow-worker**

`Only to take down airflow`

# Take down just Airflow services
docker-compose stop airflow-webserver airflow-scheduler airflow-worker airflow-init redis

docker-compose stop airflow-webserver airflow-scheduler airflow-worker redis
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker redis


# (Re-run init if you changed DB-related configs)
docker-compose run --rm airflow-init

# Bring up Airflow services
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker redis

# .env
environment:
      - AIRFLOW__CORE__EXECUTOR=${AIRFLOW__CORE__EXECUTOR}
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN}
      - AIRFLOW__CELERY__RESULT_BACKEND=${AIRFLOW__CELERY__RESULT_BACKEND}
      - AIRFLOW__CELERY__BROKER_URL=${AIRFLOW__CELERY__BROKER_URL}
      - AIRFLOW__CORE__FERNET_KEY=${AIRFLOW__CORE__FERNET_KEY}
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=${AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION}
      - AIRFLOW__CORE__LOAD_EXAMPLES=${AIRFLOW__CORE__LOAD_EXAMPLES}

To check the .env is loaded properly or not
**docker-compose config**

# Create DB User
CREATE DATABASE IF NOT EXISTS airflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'airflow_user'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON airflow.* TO 'airflow_user'@'%';
FLUSH PRIVILEGES;