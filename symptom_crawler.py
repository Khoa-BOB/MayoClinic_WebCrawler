from bs4 import BeautifulSoup
import requests
import time
import string
import os
import json
from urllib.parse import urljoin
from main import MayoClinicCrawler


class SymptomCrawlerEngine:
    """Polite crawling engine for Mayo Clinic symptoms"""

    def __init__(self, base_url='https://www.mayoclinic.org/',
                 delay=2.0, max_retries=3, output_dir='symptom_data'):
        """
        Initialize the polite crawler engine for symptoms

        Args:
            base_url: Base URL of the website
            delay: Delay between requests in seconds (default 2s)
            max_retries: Maximum number of retries for failed requests
            output_dir: Directory to save crawled data
        """
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        self.output_dir = output_dir
        self.headers = {"User-Agent": "Mozilla/5.0 (Educational crawler)"}
        self.crawler = MayoClinicCrawler(base_url=base_url, headers=self.headers)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/markdown", exist_ok=True)
        os.makedirs(f"{output_dir}/yaml", exist_ok=True)

    def fetch_with_retry(self, url):
        """Fetch URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * 2)  # Wait longer on retry
                else:
                    raise
        return None

    def get_all_symptom_links(self):
        """
        Crawl the symptoms index pages and extract all symptom links

        Returns:
            List of tuples: [(symptom_name, symptom_url), ...]
        """
        print("Fetching all symptom links...")
        all_symptoms = []

        # Iterate through A-Z index pages
        for letter in string.ascii_uppercase:
            print(f"Fetching symptoms starting with '{letter}'...")
            url = f"{self.base_url}symptoms/index?letter={letter}"

            try:
                response = self.fetch_with_retry(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all symptom links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    # Filter for actual symptom pages
                    # Pattern: /symptoms/symptom-name/basics/definition/sym-XXXXXXXX
                    if ('/symptoms/' in href and
                        '/basics/definition/' in href and
                        'index' not in href):

                        symptom_name = link.get_text(strip=True)
                        if symptom_name and len(symptom_name) > 1:
                            print(f"  {symptom_name}")
                            # Convert relative URLs to absolute
                            if href.startswith('/'):
                                href = urljoin(self.base_url, href)

                            all_symptoms.append((symptom_name, href))

                # Be polite - wait between requests
                time.sleep(self.delay)

            except Exception as e:
                print(f"Error fetching letter {letter}: {e}")
                continue

        # Remove duplicates while preserving order
        seen = set()
        unique_symptoms = []
        for name, url in all_symptoms:
            if url not in seen:
                seen.add(url)
                unique_symptoms.append((name, url))

        print(f"\nTotal unique symptoms found: {len(unique_symptoms)}")
        return unique_symptoms

    def extract_symptom_slug(self, url):
        """Extract symptom slug from URL for filename"""
        # Example: .../symptoms/abdominal-pain/basics/definition/sym-20050728
        # Returns: abdominal-pain
        parts = url.split('/symptoms/')
        if len(parts) > 1:
            slug = parts[1].split('/basics/definition/')[0]
            return slug
        return None

    def crawl_symptom(self, symptom_name, symptom_url):
        """
        Crawl a single symptom page

        Args:
            symptom_name: Name of the symptom
            symptom_url: URL of the symptom page

        Returns:
            dict: Extracted data or None if failed
        """
        try:
            print(f"Crawling: {symptom_name}")

            # Extract the path from full URL
            path = symptom_url.replace(self.base_url, '')

            # Add print mode parameter if not already present
            if '?p=' not in path:
                path += '?p=1'

            # Crawl the page
            data = self.crawler.crawl(path)

            if data and data.get('sections'):
                return data
            else:
                print(f"  Warning: No content found for {symptom_name}")
                return None

        except Exception as e:
            print(f"  Error crawling {symptom_name}: {e}")
            return None

    def save_symptom_data(self, symptom_name, symptom_url, data):
        """Save symptom data to both markdown and YAML"""
        slug = self.extract_symptom_slug(symptom_url)
        if not slug:
            slug = symptom_name.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')

        # Save as markdown
        md_path = f"{self.output_dir}/markdown/{slug}.md"
        self.crawler.export_to_markdown(data, md_path)

        # Save as YAML
        yaml_path = f"{self.output_dir}/yaml/{slug}.yaml"
        self.crawler.export_to_yaml(data, yaml_path)

        return slug

    def crawl_all_symptoms(self, limit=None, start_from=0):
        """
        Crawl all symptoms

        Args:
            limit: Maximum number of symptoms to crawl (None = all)
            start_from: Index to start from (for resuming)
        """
        # Get all symptom links
        symptoms = self.get_all_symptom_links()

        if limit:
            symptoms = symptoms[start_from:start_from + limit]
        else:
            symptoms = symptoms[start_from:]

        print(f"\nStarting crawl of {len(symptoms)} symptoms...")
        print(f"Delay between requests: {self.delay}s")
        print(f"Output directory: {self.output_dir}\n")

        # Track progress
        progress = {
            'total': len(symptoms),
            'successful': 0,
            'failed': 0,
            'failed_list': []
        }

        for idx, (symptom_name, symptom_url) in enumerate(symptoms, start=start_from + 1):
            print(f"[{idx}/{start_from + len(symptoms)}] ", end="")

            try:
                # Crawl the symptom page
                data = self.crawl_symptom(symptom_name, symptom_url)

                if data:
                    # Save the data
                    slug = self.save_symptom_data(symptom_name, symptom_url, data)
                    print(f"  ✓ Saved as {slug}")
                    progress['successful'] += 1
                else:
                    progress['failed'] += 1
                    progress['failed_list'].append((symptom_name, symptom_url))

                # Be polite - wait between requests
                time.sleep(self.delay)

            except KeyboardInterrupt:
                print("\n\nCrawling interrupted by user.")
                print(f"Progress: {progress['successful']} successful, {progress['failed']} failed")
                print(f"You can resume from index {idx}")
                break
            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                progress['failed'] += 1
                progress['failed_list'].append((symptom_name, symptom_url))
                time.sleep(self.delay)

        # Save progress report
        self.save_progress_report(progress, start_from)

        # Print summary
        print("\n" + "="*60)
        print("CRAWL SUMMARY")
        print("="*60)
        print(f"Total processed: {progress['successful'] + progress['failed']}")
        print(f"Successful: {progress['successful']}")
        print(f"Failed: {progress['failed']}")

        if progress['failed_list']:
            print("\nFailed items:")
            for name, url in progress['failed_list'][:10]:  # Show first 10
                print(f"  - {name}: {url}")
            if len(progress['failed_list']) > 10:
                print(f"  ... and {len(progress['failed_list']) - 10} more")

    def save_progress_report(self, progress, start_from):
        """Save progress report as JSON"""
        report_path = f"{self.output_dir}/crawl_report.json"
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'start_from': start_from,
            'progress': progress
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nProgress report saved to {report_path}")


if __name__ == "__main__":
    # Example usage
    engine = SymptomCrawlerEngine(
        delay=2.0,  # 2 second delay between requests
        output_dir='symptom_data'
    )

    # Test with first 5 symptoms
    print("Testing crawler with first 5 symptoms...")
    engine.crawl_all_symptoms(limit=5)

    # To crawl all symptoms:
    # engine.crawl_all_symptoms()

    # To resume from a specific index:
    # engine.crawl_all_symptoms(start_from=50)
