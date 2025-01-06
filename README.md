# Weather Dashboard ETL Pipeline

This project is an Apache Airflow DAG that fetches weather data from OpenWeatherMap API for multiple cities and stores it in AWS S3. The pipeline runs hourly, collecting temperature, humidity, and weather condition data.

## Prerequisites

- Docker and Docker Compose
- OpenWeatherMap API key
- AWS account with S3 access
- Python 3.7+

## Project Structure

```
weather-airflow/
├── dags/
│   └── weather_dag.py
├── docker-compose.yaml
├── requirements.txt
├── .env
├── .env.example
└── .gitignore
```

## Environment Variables

Create a `.env` file with the following variables:

```
OPENWEATHER_API_KEY=your_api_key_here
AWS_BUCKET_NAME=your_bucket_name_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd weather-airflow
```

2. Create and configure your `.env` file using `.env.example` as a template.

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Start the Airflow services:
```bash
docker-compose up -d
```

## DAG Overview

The DAG (`weather_dag.py`) consists of three main tasks:

1. `create_bucket`: Creates an S3 bucket if it doesn't exist
2. `fetch_weather_data`: Fetches weather data for Philadelphia, Seattle, and New York
3. `save_to_s3`: Saves the weather data to S3 in JSON format

The pipeline runs hourly and saves data in the format:
```
s3://your-bucket-name/weather-data/city-YYYYMMDD-HHMMSS.json
```

## Accessing the Airflow UI

1. Navigate to `http://localhost:8080` in your web browser
2. Login with:
   - Username: admin
   - Password: admin

## Data Format

The weather data is stored in JSON format with the following structure:

```json
{
  "main": {
    "temp": 72.5,
    "feels_like": 71.2,
    "humidity": 65
  },
  "weather": [
    {
      "description": "scattered clouds"
    }
  ],
  "timestamp": "20250106-153000"
}
```

## Monitoring and Maintenance

- View logs in the Airflow UI or using:
```bash
docker-compose logs -f airflow-scheduler
```

- Stop the services:
```bash
docker-compose down
```

## Customization

To add or modify cities, update the `CITIES` list in `weather_dag.py`:

```python
CITIES = ["Philadelphia", "Seattle", "New York"]
```

## Troubleshooting

Common issues and solutions:

1. **API Key Invalid**: Verify your OpenWeatherMap API key is correctly set in `.env`
2. **AWS Credentials**: Ensure AWS credentials have proper S3 permissions
3. **Docker Issues**: Make sure all required ports are available (8080 for Airflow UI)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.