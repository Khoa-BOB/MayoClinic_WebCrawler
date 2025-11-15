#!/usr/bin/env python3
"""
Script to run the Mayo Clinic symptom crawler

Usage:
    # Crawl all symptoms:
    python run_symptom_crawler.py

    # Crawl first 10 symptoms (for testing):
    python run_symptom_crawler.py --limit 10

    # Resume from a specific index:
    python run_symptom_crawler.py --start-from 50

    # Combine options:
    python run_symptom_crawler.py --start-from 20 --limit 30
"""

import argparse
from symptom_crawler import SymptomCrawlerEngine


def main():
    parser = argparse.ArgumentParser(
        description='Crawl Mayo Clinic symptoms from A to Z',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl all symptoms:
  python run_symptom_crawler.py

  # Test with first 5 symptoms:
  python run_symptom_crawler.py --limit 5

  # Resume from symptom #50:
  python run_symptom_crawler.py --start-from 50

  # Crawl 20 symptoms starting from #30:
  python run_symptom_crawler.py --start-from 30 --limit 20
        """
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of symptoms to crawl (default: all)'
    )

    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Index to start from (default: 0, for resuming interrupted crawls)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='symptom_data',
        help='Output directory for crawled data (default: symptom_data)'
    )

    args = parser.parse_args()

    # Create crawler engine
    print(f"Initializing Mayo Clinic Symptom Crawler")
    print(f"Output directory: {args.output_dir}")
    print(f"Delay between requests: {args.delay}s")
    print("-" * 60)

    engine = SymptomCrawlerEngine(
        delay=args.delay,
        output_dir=args.output_dir
    )

    # Start crawling
    engine.crawl_all_symptoms(
        limit=args.limit,
        start_from=args.start_from
    )

    print("\n" + "=" * 60)
    print("Crawling complete!")
    print(f"Results saved to: {args.output_dir}")
    print("  - Markdown files: {}/markdown/".format(args.output_dir))
    print("  - YAML files: {}/yaml/".format(args.output_dir))
    print("  - Progress report: {}/crawl_report.json".format(args.output_dir))
    print("=" * 60)


if __name__ == "__main__":
    main()
