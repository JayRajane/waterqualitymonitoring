pip3 install cryptography

How to generate a valid Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

mkdir -p airflow/dags airflow/logs

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

<!-- Airflow Setup -->
# Install Airflow (only for local setup)
pip3 install apache-airflow==2.9.1 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-3.10.txt"

mkdir airflow
mkdir -p airflow/dags airflow/logs airflow/plugins
touch airflow/docker-compose.yml
touch airflow/.env

AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CORE__FERNET_KEY=your_generated_key_here
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=mysql+mysqldb://airflow_user:Bliss%40Jarvis20@host.docker.internal:3306/airflow
AIRFLOW__CELERY__RESULT_BACKEND=db+mysql://airflow_user:Bliss%40Jarvis20@host.docker.internal:3306/airflow
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Initialize a new Airflow project
export AIRFLOW_HOME=/Volumes/SSD/Code/Backend/water_monitoring_system/airflow
# With Docker:
docker-compose run --rm airflow-init
docker-compose up -d


 # Without docker: airflow db init
echo "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" -> mysql+pymysql://root:Jarvis%40786@localhost:3306/airflow
pip3 install pymysql
airflow db reset --yes
airflow db init
# Create Admin User (local only)
airflow users create \
  --username admin \
  --password admin \
  --firstname Air \
  --lastname Flow \
  --role Admin \
  --email admin@example.com

# Start Airflow services
airflow scheduler & airflow webserver --port 8080
pkill -f airflow
To kill all serices using port
**lsof -i :8080**
lsof -i :8080
kill -9 <PID>
kill -9 $(lsof -ti :8080)

pkill -f "airflow scheduler" && pkill -f "airflow webserver"

# TO Schedule/Delete the Dags
airflow dags delete {dag_id} --yes
airflow dags trigger {dag_id}

to stop all services
# Created a sample start_airflow.sh
chmod +x start_airflow.sh

# To run airflow
./start_airflow.sh

airflow scheduler & airflow webserver --port 8080 & airflow celery worker --concurrency 4 &
For local restart to apply changes for .env
docker-compose up -d --force-recreate airflow-webserver airflow-scheduler airflow-worker

# Changes in Custom Python Modules (e.g. airflow/plugins/ or custom_operators/)
docker-compose restart airflow-webserver airflow-scheduler airflow-worker

# Changes to docker-compose.yml
docker-compose up -d --force-recreate airflow-worker

docker exec -it airflow-webserver pip install pandas

docker-compose build airflow-webserver
docker-compose up -d airflow-webserver

mysql -u root -p
Jarvis@786

https://chatgpt.com/c/68572895-6a00-8004-9362-fc8e08964794