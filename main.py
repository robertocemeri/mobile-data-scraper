import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from openai import OpenAI
import os
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime
from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
VECTOR_STORE_ID = os.getenv('VECTOR_STORE_ID')

# Add to existing environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([OPENAI_API_KEY, ASSISTANT_ID, VECTOR_STORE_ID, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Please set all required environment variables in .env file")

class OpenAIUploader:
    def __init__(self, api_key: str, assistant_id: str, vector_store_id: str):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id

    def upload_file(self, file_path: str) -> str:
        """Upload a file to OpenAI and attach it to the assistant"""
        try:
            # Upload the file
            with open(file_path, 'rb') as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
                logger.info(f"Uploaded file: {uploaded_file}")

            vector_store_files = self.client.beta.vector_stores.files.list(
                vector_store_id=self.vector_store_id
            )
            logger.info(f"Retrieved vector store files: {vector_store_files}")
            # Delete all files from vector store
            for file in vector_store_files.data:
                self.client.beta.vector_stores.files.delete(
                    vector_store_id=self.vector_store_id,
                    file_id=file.id
                )
            logger.info("Deleted all files from vector store")


            # Attach the uploaded file to the vector store
            self.client.beta.vector_stores.files.create(
                vector_store_id=self.vector_store_id,
                file_id=uploaded_file.id
            )
            logger.info(f"Attached file to vector store: {self.vector_store_id}")
            logger.info(f"Successfully uploaded and attached file: {file_path}")
            return uploaded_file.id
        except Exception as e:
            logger.error(f"Error uploading file to OpenAI: {str(e)}")
            raise

class WebScraper:
    def __init__(self, max_workers: int = 5, timeout: int = 10):
        self.session = self._create_session(timeout)
        self.max_workers = max_workers

    def _create_session(self, timeout: int) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = timeout
        return session

    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page, returning BeautifulSoup object"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def get_related_urls(self, page_url: str, topic: str) -> List[str]:
        """Get URLs related to the specified topic from the page"""
        soup = self._fetch_page(page_url)
        if not soup:
            return []

        page_title = soup.title.string if soup.title else "No title found"
        logger.info(f"Processing page: {page_title}")

        related_urls = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if topic.lower() in href.lower() or topic.lower() in link.text.lower():
                full_url = urljoin(page_url, href)
                related_urls.append(full_url)

        logger.info(f"Found {len(related_urls)} related URLs for topic '{topic}' on {page_url}")
        return list(set(related_urls))  # Remove duplicates

    def extract_data_from_url(self, url: str) -> Optional[Dict]:
        """Extract relevant data from a URL"""
        soup = self._fetch_page(url)
        if not soup:
            return None

        return {
            'title': soup.title.string if soup.title else "No title found",
            'description': self._get_meta_description(soup),
            'body': soup.get_text(strip=True)
        }

    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from BeautifulSoup object"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'] if meta and 'content' in meta.attrs else "No description found"

    def scrape_data_from_urls(self, page_url: str, topic: str) -> List[Dict]:
        """Main scraping function using thread pool for parallel processing"""
        related_urls = self.get_related_urls(page_url, topic)
        data_objects = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.extract_data_from_url, url): url 
                for url in related_urls
            }

            for future in future_to_url:
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        data_objects.append({'url': url, 'data': data})
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")

        return data_objects

def get_target_sites() -> List[Tuple[str, str]]:
    """Fetch target sites from Supabase"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch all target sites from the 'target_sites' table
        response = supabase.table('target_sites').select("url", "topic").execute()
        
        # Convert the response to the required format
        target_sites = [(site['url'], site['topic']) for site in response.data]
        
        logger.info(f"Retrieved {len(target_sites)} target sites from Supabase")
        return target_sites
    except Exception as e:
        logger.error(f"Error fetching target sites from Supabase: {str(e)}")
        raise

def job():
    """Main job to be run daily"""
    logger.info(f"Starting scheduled job at {datetime.now()}")
    try:
        # Get target sites from Supabase
        target_sites = get_target_sites()
        
        logger.info(target_sites)

        if not target_sites:
            logger.error("No target sites found in Supabase")
            return

        scraper = WebScraper()
        all_data = []

        # Scrape data from all sites
        for site_url, topic in target_sites:
            logger.info(f"Processing site: {site_url}")
            site_data = scraper.scrape_data_from_urls(site_url, topic)
            all_data.extend(site_data)

        # Save results with normalized line endings
        output_file = 'data_objects.json'
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
            f.write('\n')  # Add final newline

        logger.info(f"Data saved to {output_file}")

        # Upload to OpenAI Assistant
        uploader = OpenAIUploader(OPENAI_API_KEY, ASSISTANT_ID, VECTOR_STORE_ID)
        file_id = uploader.upload_file(output_file)
        logger.info(f"Successfully uploaded to OpenAI. File ID: {file_id}")
        
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")
        # You might want to add notification logic here for failed jobs

def main():
    """Setup and run the scheduler"""
    logger.info("Starting scheduler...")
    
    # Schedule the job to run at 2 AM every day
    schedule.every().day.at("02:00").do(job)
    
    # Run the job immediately on startup (optional)
    logger.info("Running initial job...")
    job()
    
    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
