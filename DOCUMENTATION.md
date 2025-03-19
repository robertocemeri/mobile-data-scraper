# Project Development Documentation
Date: [Current Date]

## Project Overview
We've developed a web scraper system that focuses on collecting mobile-related data from Swiss telecommunications providers (Swisscom, Sunrise, and Salt). The system integrates with OpenAI's vector store and uses Supabase for managing target sites.

## Components Implemented

### 1. Core Scraping System (`main.py`)
- Implemented a multi-threaded web scraper
- Added retry mechanisms for reliable scraping
- Integrated BeautifulSoup for HTML parsing
- Set up scheduled execution (daily at 2 AM)

### 2. OpenAI Integration
- Created `OpenAIUploader` class for file management
- Implemented vector store integration
- Added file cleanup mechanisms

### 3. Database Integration
- Set up Supabase connection
- Created target sites table
- Implemented site management functionality

### 4. Configuration
- Set up environment variables
- Created Docker configuration
- Implemented logging system

## Key Features Implemented

1. **Web Scraping**
   - Multi-threaded processing
   - URL discovery based on topics
   - Content extraction (title, description, body)
   - Error handling and retries

2. **Data Processing**
   - JSON output formatting
   - Data normalization
   - Duplicate URL removal

3. **Automation**
   - Scheduled execution
   - Continuous monitoring
   - Automatic file management

## Current Data Structure

The system generates data in the following format:
```json
{
    "url": "https://example.com",
    "data": {
        "title": "Page Title",
        "description": "Meta Description",
        "body": "Page Content"
    }
}
```

## Environment Configuration

```env
OPENAI_API_KEY=<key>
ASSISTANT_ID=<id>
VECTOR_STORE_ID=<id>
SUPABASE_URL=<url>
SUPABASE_KEY=<key>
```

## Database Schema

```sql
create table if not exists target_sites (
    id uuid default uuid_generate_v4() primary key,
    url text not null,
    topic text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Current Target Sites
- Swisscom (https://www.swisscom.ch)
- Sunrise (https://www.sunrise.ch)
- Salt (https://www.salt.ch)

## Deployment Options

1. **Local Deployment**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

2. **Docker Deployment**
   ```bash
   docker compose up -d
   ```

## Testing Status
- Basic functionality testing completed
- Successfully scraping target sites
- OpenAI integration verified
- Supabase connection confirmed

## Known Limitations
1. Rate limiting considerations for target sites
2. Memory usage with large datasets
3. Dependency on external services (OpenAI, Supabase)

## Next Steps
1. Implement more robust error notification
2. Add data validation
3. Enhance content filtering
4. Add monitoring dashboard
5. Implement backup mechanisms

## Technical Debt
1. Need to add unit tests
2. Documentation for API responses
3. Performance optimization for large datasets
4. Security hardening

## Dependencies
```text
requests
beautifulsoup4
openai
python-dotenv
schedule
supabase
```

## Monitoring and Maintenance
- Log files location: Application root directory
- Data output: `data_objects.json`
- Docker container: `web-scraper`
- Scheduled run time: 2 AM daily

## Backup and Recovery
- Data is stored in:
  - Supabase database
  - Local JSON file
  - OpenAI vector store

## Security Considerations
1. API keys stored in environment variables
2. Docker container isolation
3. Rate limiting implementation
4. Error handling for sensitive data

## Support and Troubleshooting
1. Check application logs
2. Monitor Docker container status
3. Verify Supabase connection
4. Confirm OpenAI API status

## Version Control
- All code maintained in Git repository
- Docker images versioned
- Environment configurations tracked

This documentation represents the current state of the project as of today's implementation. It should be updated as new features are added or modifications are made to the existing functionality.