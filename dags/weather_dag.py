from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import json
import boto3
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variables
CITIES = ["Philadelphia", "Seattle", "New York"]
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

def create_bucket_if_not_exists(**context):
    """Create S3 bucket if it doesn't exist"""
    s3_client = boto3.client('s3')
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} exists")
    except:
        print(f"Creating bucket {BUCKET_NAME}")
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
            print(f"Successfully created bucket {BUCKET_NAME}")
        except Exception as e:
            print(f"Error creating bucket: {e}")
            raise

def fetch_weather_data(**context):
    """Fetch weather data for all cities"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    all_weather_data = {}
    
    for city in CITIES:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "imperial"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # Print weather information
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            
            print(f"\nWeather for {city}:")
            print(f"Temperature: {temp}°F")
            print(f"Feels like: {feels_like}°F")
            print(f"Humidity: {humidity}%")
            print(f"Conditions: {description}")
            
            all_weather_data[city] = weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data for {city}: {e}")
    
    # Push the collected data to XCom
    context['task_instance'].xcom_push(key='weather_data', value=all_weather_data)

def save_to_s3(**context):
    """Save weather data to S3 bucket"""
    # Pull weather data from XCom
    weather_data = context['task_instance'].xcom_pull(task_ids='fetch_weather_data', key='weather_data')
    
    if not weather_data:
        raise Exception("No weather data available")
    
    s3_client = boto3.client('s3')
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    for city, city_data in weather_data.items():
        file_name = f"weather-data/{city}-{timestamp}.json"
        try:
            city_data['timestamp'] = timestamp
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=json.dumps(city_data),
                ContentType='application/json'
            )
            print(f"Successfully saved data for {city} to S3")
        except Exception as e:
            print(f"Error saving {city} data to S3: {e}")
            raise

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

# Create the DAG
with DAG(
    'weather_dashboard',
    default_args=default_args,
    description='Fetch and store weather data for multiple cities',
    schedule_interval='@hourly',  # Run every hour
    catchup=False,
) as dag:
    
    # Create tasks
    create_bucket_task = PythonOperator(
        task_id='create_bucket',
        python_callable=create_bucket_if_not_exists,
    )
    
    fetch_weather_task = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_weather_data,
    )
    
    save_to_s3_task = PythonOperator(
        task_id='save_to_s3',
        python_callable=save_to_s3,
    )
    
    # Set task dependencies
    create_bucket_task >> fetch_weather_task >> save_to_s3_task