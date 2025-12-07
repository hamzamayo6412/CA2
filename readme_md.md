# COVID-19 Data Dashboard - Flask Web App

A comprehensive Flask web application that fetches COVID-19 statistics from RapidAPI, processes and cleans the data, stores it in SQLite3 database, and provides an interactive web interface for data visualization and querying.

## Features

✅ **Data Fetching**: Retrieves 500+ COVID-19 records from RapidAPI  
✅ **Data Processing**: Cleans, transforms, and preprocesses raw data  
✅ **Database Storage**: Stores data in SQLite3 with proper schema  
✅ **Interactive UI**: Real-time filtering, sorting, and pagination  
✅ **Statistics Dashboard**: Live summary cards with key metrics  
✅ **Data Visualization**: Chart.js powered bar charts  
✅ **RESTful API**: Complete API endpoints for data access  

## Project Structure

```
flask-covid-app/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Example environment file
├── covid_data.db         # SQLite database (auto-generated)
│
└── templates/
    └── index.html        # Frontend dashboard
```

## Installation

### 1. Clone or Download the Project

```bash
mkdir flask-covid-app
cd flask-covid-app
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get RapidAPI Key

1. Go to [RapidAPI COVID-193 API](https://rapidapi.com/api-sports/api/covid-193)
2. Sign up for a free account
3. Subscribe to the free plan
4. Copy your API key

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
RAPIDAPI_KEY=your_actual_api_key_here
```

### 6. Create Templates Directory

```bash
mkdir templates
# Place the index.html file in this directory
```

## Running the Application

### Start the Flask Server

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Using the Application

1. **Open Browser**: Navigate to `http://localhost:5000`
2. **Fetch Data**: Click "Fetch Fresh Data from API" button
3. **Explore Data**: Use filters to search and sort records
4. **View Charts**: Scroll down to see top 10 countries visualization

## API Endpoints

### 1. Fetch and Store Data
```
GET /api/fetch-data
```
Fetches data from RapidAPI and stores in database

### 2. Get Records
```
GET /api/records?page=1&per_page=10&country=USA&continent=North-America&sort_by=total_cases&order=desc
```
Returns paginated records with filtering and sorting

### 3. Get Statistics
```
GET /api/statistics
```
Returns summary statistics (total cases, deaths, recovered)

### 4. Get Continents
```
GET /api/continents
```
Returns list of unique continents

### 5. Get Top Countries
```
GET /api/top-countries?metric=total_cases&limit=10
```
Returns top countries by specified metric

## Database Schema

### CovidRecord Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| country | String(100) | Country name |
| country_code | String(10) | Country code |
| continent | String(50) | Continent name |
| population | Integer | Total population |
| total_cases | Integer | Total COVID cases |
| new_cases | Integer | New cases |
| total_deaths | Integer | Total deaths |
| new_deaths | Integer | New deaths |
| total_recovered | Integer | Total recovered |
| active_cases | Integer | Active cases |
| critical_cases | Integer | Critical cases |
| cases_per_million | Float | Cases per million |
| deaths_per_million | Float | Deaths per million |
| total_tests | Integer | Total tests conducted |
| tests_per_million | Float | Tests per million |
| date_recorded | DateTime | Record timestamp |

## Data Processing Pipeline

### 1. Fetch Data
- Connects to RapidAPI COVID-193 endpoint
- Retrieves latest statistics for all countries
- Handles API errors and rate limits

### 2. Clean & Transform
- Extracts relevant fields from raw JSON
- Removes invalid entries (Unknown, All)
- Normalizes country names (strip whitespace)
- Converts null values to 0 or 0.0
- Creates country codes (first 3 letters uppercase)
- Limits to 500 records as requested

### 3. Store in Database
- Checks for existing records by country
- Updates existing records with new data
- Inserts new records
- Maintains data integrity with transactions

## Features Breakdown

### Interactive Filtering
- **Country Search**: Real-time text search
- **Continent Filter**: Dropdown selection
- **Sort Options**: Multiple columns (cases, deaths, recovered, etc.)
- **Sort Order**: Ascending/Descending
- **Pagination**: 10, 25, 50, 100 records per page

### Statistics Dashboard
- Total Records Count
- Global Total Cases
- Global Total Deaths
- Global Total Recovered
- Active Cases Worldwide

### Data Visualization
- Top 10 countries by total cases
- Interactive Chart.js bar chart
- Responsive design
- Formatted numbers with commas

## Technologies Used

- **Backend**: Flask 3.1.0
- **Database**: SQLite3 with Flask-SQLAlchemy 3.1.1
- **API**: RapidAPI COVID-193
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **HTTP Client**: Requests 2.32.3
- **Environment**: python-dotenv 1.0.1

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## Error Handling

- API connection errors
- Database transaction errors
- Invalid query parameters
- Missing environment variables
- Data validation errors

## Future Enhancements

- Export data to CSV/Excel
- Historical data tracking
- Email alerts for data updates
- User authentication
- Advanced analytics
- More chart types
- Real-time updates with WebSocket
- Data comparison over time

## Troubleshooting

### Database Issues
```bash
# Delete and recreate database
rm covid_data.db
python app.py
```

### API Key Issues
- Verify your RapidAPI key is correct
- Check subscription status on RapidAPI
- Ensure no spaces in .env file

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## License

This project is open source and available for educational purposes.

## Credits

- COVID-19 Data: [RapidAPI COVID-193](https://rapidapi.com/api-sports/api/covid-193)
- Inspired by: [flask-app repository](https://github.com/Sameer-Jahangier99/flask-app)
- Charts: Chart.js
- Framework: Flask

## Support

For issues or questions, please check:
1. Verify all dependencies are installed
2. Check .env file configuration
3. Ensure templates folder exists
4. Review console for error messages

---
