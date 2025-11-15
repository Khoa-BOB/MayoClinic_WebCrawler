#!/usr/bin/env python3
"""
Example script to run the Mayo Clinic polite crawler engine

Usage:
    # Diseases and Conditions:
    python run_crawler.py --type diseases --mode test      # Test with 5 diseases
    python run_crawler.py --type diseases --mode sample    # Crawl 50 diseases
    python run_crawler.py --type diseases --mode all       # Crawl all diseases
    python run_crawler.py --type diseases --mode resume --start 100  # Resume from index 100

    # Drugs and Supplements:
    python run_crawler.py --type drugs --mode test         # Test with 5 drugs/supplements
    python run_crawler.py --type drugs --mode sample       # Crawl 50 drugs/supplements
    python run_crawler.py --type drugs --mode all          # Crawl all drugs/supplements
    python run_crawler.py --type drugs --mode resume --start 100  # Resume from index 100
"""

import argparse
from crawler_engine import PoliteCrawlerEngine
from drug_supplement_crawler import DrugSupplementCrawlerEngine


def main():
    parser = argparse.ArgumentParser(description='Mayo Clinic Crawler for Diseases and Drugs/Supplements')
    parser.add_argument('--type', choices=['diseases', 'drugs'],
                        default='diseases', help='Type of content to crawl')
    parser.add_argument('--mode', choices=['test', 'sample', 'all', 'resume'],
                        default='test', help='Crawling mode')
    parser.add_argument('--start', type=int, default=0,
                        help='Starting index (for resume mode)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Maximum number of items to crawl')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay between requests in seconds')
    parser.add_argument('--output', default=None,
                        help='Output directory (defaults based on type)')

    args = parser.parse_args()

    # Set default output directory based on type
    if args.output is None:
        args.output = 'mayo_clinic_data' if args.type == 'diseases' else 'drug_supplement_data'

    # Initialize appropriate crawler engine
    if args.type == 'diseases':
        engine = PoliteCrawlerEngine(
            delay=args.delay,
            output_dir=args.output
        )
        content_type = "diseases/conditions"
        crawl_method = engine.crawl_all_diseases
    else:  # drugs
        engine = DrugSupplementCrawlerEngine(
            delay=args.delay,
            output_dir=args.output
        )
        content_type = "drugs/supplements"
        crawl_method = engine.crawl_all_drugs_supplements

    print("="*60)
    print("MAYO CLINIC POLITE CRAWLER ENGINE")
    print("="*60)
    print(f"Content Type: {content_type}")
    print(f"Mode: {args.mode}")
    print(f"Delay: {args.delay}s between requests")
    print(f"Output: {args.output}/")
    print("="*60)
    print()

    # Execute based on mode
    if args.mode == 'test':
        print(f"Running in TEST mode - crawling first 5 {content_type}")
        crawl_method(limit=5)

    elif args.mode == 'sample':
        print(f"Running in SAMPLE mode - crawling first 50 {content_type}")
        crawl_method(limit=50)

    elif args.mode == 'all':
        print(f"Running in ALL mode - crawling all {content_type}")
        print("This may take several hours. Press Ctrl+C to stop.")
        crawl_method()

    elif args.mode == 'resume':
        print(f"Running in RESUME mode - starting from index {args.start}")
        crawl_method(start_from=args.start, limit=args.limit)

    print("\nCrawling complete!")


if __name__ == "__main__":
    main()
