from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///covid_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class CovidRecord(db.Model):
    __tablename__ = 'covid_records'
    
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10))
    continent = db.Column(db.String(50))
    population = db.Column(db.Integer)
    total_cases = db.Column(db.Integer)
    new_cases = db.Column(db.Integer)
    total_deaths = db.Column(db.Integer)
    new_deaths = db.Column(db.Integer)
    total_recovered = db.Column(db.Integer)
    active_cases = db.Column(db.Integer)
    critical_cases = db.Column(db.Integer)
    cases_per_million = db.Column(db.Float)
    deaths_per_million = db.Column(db.Float)
    total_tests = db.Column(db.Integer)
    tests_per_million = db.Column(db.Float)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'country_code': self.country_code,
            'continent': self.continent,
            'population': self.population,
            'total_cases': self.total_cases,
            'new_cases': self.new_cases,
            'total_deaths': self.total_deaths,
            'new_deaths': self.new_deaths,
            'total_recovered': self.total_recovered,
            'active_cases': self.active_cases,
            'critical_cases': self.critical_cases,
            'cases_per_million': self.cases_per_million,
            'deaths_per_million': self.deaths_per_million,
            'total_tests': self.total_tests,
            'tests_per_million': self.tests_per_million,
            'date_recorded': self.date_recorded.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create tables
with app.app_context():
    db.create_all()

def fetch_covid_data():
    """Fetch COVID-19 data from RapidAPI"""
    url = "https://covid-193.p.rapidapi.com/statistics"
    
    headers = {
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY', 'your_api_key_here'),
        "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def clean_and_transform_data(raw_data):
    """Clean, transform and preprocess the data"""
    if not raw_data or 'response' not in raw_data:
        return []
    
    cleaned_records = []
    
    for record in raw_data['response'][:500]:  # Limit to 500 records
        try:
            # Extract and clean data
            country_name = record.get('country', 'Unknown')
            
            # Skip invalid entries
            if country_name in ['All', 'Unknown']:
                continue
            
            # Transform and clean numeric values
            cases = record.get('cases', {})
            deaths = record.get('deaths', {})
            tests = record.get('tests', {})
            
            cleaned_record = {
                'country': country_name.strip(),
                'country_code': record.get('country', '')[:3].upper(),
                'continent': record.get('continent', 'Unknown'),
                'population': record.get('population') or 0,
                'total_cases': cases.get('total') or 0,
                'new_cases': cases.get('new') or 0,
                'total_deaths': deaths.get('total') or 0,
                'new_deaths': deaths.get('new') or 0,
                'total_recovered': cases.get('recovered') or 0,
                'active_cases': cases.get('active') or 0,
                'critical_cases': cases.get('critical') or 0,
                'cases_per_million': cases.get('1M_pop') or 0.0,
                'deaths_per_million': deaths.get('1M_pop') or 0.0,
                'total_tests': tests.get('total') or 0,
                'tests_per_million': tests.get('1M_pop') or 0.0
            }
            
            cleaned_records.append(cleaned_record)
            
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    
    return cleaned_records

def store_data_in_db(records):
    """Store cleaned data in SQLite database"""
    count = 0
    try:
        for record in records:
            # Check if record already exists
            existing = CovidRecord.query.filter_by(
                country=record['country']
            ).first()
            
            if existing:
                # Update existing record
                for key, value in record.items():
                    setattr(existing, key, value)
                existing.date_recorded = datetime.utcnow()
            else:
                # Create new record
                new_record = CovidRecord(**record)
                db.session.add(new_record)
            
            count += 1
        
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        print(f"Error storing data: {e}")
        return 0

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/api/fetch-data', methods=['GET'])
def fetch_and_store():
    """API endpoint to fetch data from RapidAPI and store in database"""
    try:
        # Fetch data
        raw_data = fetch_covid_data()
        if not raw_data:
            return jsonify({'error': 'Failed to fetch data from API'}), 500
        
        # Clean and transform
        cleaned_records = clean_and_transform_data(raw_data)
        
        # Store in database
        stored_count = store_data_in_db(cleaned_records)
        
        return jsonify({
            'success': True,
            'message': f'Successfully fetched and stored {stored_count} records',
            'records_count': stored_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records', methods=['GET'])
def get_records():
    """Get records with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        country = request.args.get('country', '')
        continent = request.args.get('continent', '')
        sort_by = request.args.get('sort_by', 'total_cases')
        order = request.args.get('order', 'desc')
        
        # Build query
        query = CovidRecord.query
        
        # Apply filters
        if country:
            query = query.filter(CovidRecord.country.ilike(f'%{country}%'))
        if continent and continent != 'all':
            query = query.filter(CovidRecord.continent == continent)
        
        # Apply sorting
        if order == 'desc':
            query = query.order_by(db.desc(getattr(CovidRecord, sort_by)))
        else:
            query = query.order_by(db.asc(getattr(CovidRecord, sort_by)))
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'records': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get summary statistics"""
    try:
        total_records = CovidRecord.query.count()
        total_cases = db.session.query(db.func.sum(CovidRecord.total_cases)).scalar() or 0
        total_deaths = db.session.query(db.func.sum(CovidRecord.total_deaths)).scalar() or 0
        total_recovered = db.session.query(db.func.sum(CovidRecord.total_recovered)).scalar() or 0
        
        return jsonify({
            'total_records': total_records,
            'total_cases': total_cases,
            'total_deaths': total_deaths,
            'total_recovered': total_recovered,
            'active_cases': total_cases - total_deaths - total_recovered
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/continents', methods=['GET'])
def get_continents():
    """Get list of unique continents"""
    try:
        continents = db.session.query(CovidRecord.continent)\
            .distinct()\
            .filter(CovidRecord.continent != 'Unknown')\
            .all()
        return jsonify({
            'continents': [c[0] for c in continents if c[0]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-countries', methods=['GET'])
def get_top_countries():
    """Get top 10 countries by cases"""
    try:
        metric = request.args.get('metric', 'total_cases')
        limit = request.args.get('limit', 10, type=int)
        
        records = CovidRecord.query\
            .order_by(db.desc(getattr(CovidRecord, metric)))\
            .limit(limit)\
            .all()
        
        return jsonify({
            'countries': [record.to_dict() for record in records]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)