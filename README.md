# Web Scraper with OpenAI Integration

A Python-based web scraper that collects data from specified websites, processes it, and uploads it to OpenAI's vector store. The scraper runs on a schedule and integrates with Supabase for target site management.

## Features

- Automated web scraping with retry mechanisms and error handling
- Multi-threaded processing for improved performance
- Integration with OpenAI's vector store
- Supabase database integration for target site management
- Scheduled execution (daily at 2 AM)
- Docker support for containerized deployment
- Comprehensive logging

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- OpenAI API key
- Supabase account and credentials
- Assistant ID and Vector Store ID from OpenAI

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
ASSISTANT_ID=your_assistant_id
VECTOR_STORE_ID=your_vector_store_id
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the Supabase table:
   - Go to Supabase SQL editor
   - Run the following SQL:
```sql
create table if not exists target_sites (
    id uuid default uuid_generate_v4() primary key,
    url text not null,
    topic text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create index if not exists target_sites_url_idx on target_sites(url);
```

### Docker Setup

1. Build the Docker image:
```bash
docker compose build
```

## Usage

### Running Locally

```bash
python main.py
```

### Running with Docker

```bash
docker compose up -d
```

View logs:
```bash
docker compose logs -f
```

Stop the container:
```bash
docker compose down
```

## Adding Target Sites

Use the provided `setup_supabase.py` script to add target sites:

```bash
python setup_supabase.py
```

Or manually insert sites into Supabase:

```sql
insert into target_sites (url, topic) values
    ('https://www.swisscom.ch/en/residential.html', 'Mobile'),
    ('https://www.sunrise.ch/en/home', 'Mobile'),
    ('https://www.salt.ch/en', 'Mobile');
```

## Project Structure

```
.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── main.py
├── setup_supabase.py
├── check_supabase.py
└── .env
```

## Output

The scraper generates a `data_objects.json` file containing the scraped data. This file is automatically uploaded to OpenAI's vector store for further processing.

## Scheduling

The scraper runs:
- Immediately upon startup
- Daily at 2 AM
- Continuously monitors for scheduled runs

## Error Handling

- Comprehensive logging system
- Retry mechanism for failed requests
- Exception handling for various scenarios

## Monitoring

Monitor the application through:
- Application logs
- Generated `data_objects.json` file
- OpenAI dashboard for file uploads
- Supabase dashboard for database operations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your chosen license]

## Support

For support, please [your contact information or support process]