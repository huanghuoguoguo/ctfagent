#!/usr/bin/env python3
"""
DuckDuckGo Lite Search Script
Search the web using DuckDuckGo's lite interface.

Usage:
    python3 ddg_search.py "query string" [--limit N] [--output file.md]
"""

import argparse
import re
import sys
import urllib.parse
from typing import List, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required dependencies not installed.")
    print("Run: pip3 install requests beautifulsoup4")
    sys.exit(1)


def search_duckduckgo(query: str, limit: int = 10) -> List[dict]:
    """
    Search DuckDuckGo lite and return results.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of dicts with 'title', 'url', 'snippet' keys
    """
    results = []

    # DuckDuckGo lite endpoint
    base_url = "https://lite.duckduckgo.com/lite"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    # First request to get the search form and any required tokens
    session = requests.Session()

    try:
        # Post the search query
        data = {
            "q": query,
            "kl": "us-en",  # Region setting
        }

        response = session.post(base_url, data=data, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # DuckDuckGo lite results are in table rows
        # Each result has a link and snippet
        rows = soup.find_all('tr')

        i = 0
        while i < len(rows) and len(results) < limit:
            row = rows[i]

            # Look for result link
            link_cell = row.find('a', class_='result-link')
            if link_cell:
                title = link_cell.get_text(strip=True)
                url = link_cell.get('href', '')

                # The snippet is usually in the next row or in a snippet class
                snippet = ""
                if i + 1 < len(rows):
                    next_row = rows[i + 1]
                    snippet_cell = next_row.find('td', class_='result-snippet')
                    if snippet_cell:
                        snippet = snippet_cell.get_text(strip=True)
                        i += 1  # Skip the snippet row in next iteration

                # Clean up the URL if it's a redirect
                if url.startswith('/'):
                    # Extract actual URL from DuckDuckGo redirect
                    match = re.search(r'uddg=([^&]+)', url)
                    if match:
                        url = urllib.parse.unquote(match.group(1))

                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })

            i += 1

        # If no results found with class-based parsing, try alternative selectors
        if not results:
            # Try finding all links in result rows
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href and not href.startswith('#') and not href.startswith('/'):
                    title = link.get_text(strip=True)
                    if title and len(title) > 5:  # Filter out short/navigation links
                        # Look for parent row for snippet
                        parent_row = link.find_parent('tr')
                        snippet = ""
                        if parent_row:
                            next_sibling = parent_row.find_next_sibling('tr')
                            if next_sibling:
                                snippet = next_sibling.get_text(strip=True)

                        if len(results) < limit:
                            results.append({
                                'title': title,
                                'url': href,
                                'snippet': snippet[:200]  # Limit snippet length
                            })

    except requests.RequestException as e:
        print(f"Error searching DuckDuckGo: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []

    return results[:limit]


def format_markdown(results: List[dict], query: str) -> str:
    """Format results as Markdown."""
    lines = [
        f"# Search Results: {query}",
        "",
        f"*Query: `{query}`*",
        "",
        "---",
        ""
    ]

    for i, result in enumerate(results, 1):
        lines.append(f"## {i}. {result['title']}")
        lines.append("")
        lines.append(f"**URL:** {result['url']}")
        lines.append("")
        if result['snippet']:
            lines.append(f"{result['snippet']}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search DuckDuckGo from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 ddg_search.py "python pickle RCE"
    python3 ddg_search.py "CVE-2021-44228" --limit 5
    python3 ddg_search.py "nginx reverse proxy config" --output results.md
        """
    )

    parser.add_argument(
        "query",
        help="Search query string"
    )

    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Save results to file (Markdown format)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Perform search
    print(f"Searching DuckDuckGo for: {args.query}", file=sys.stderr)
    results = search_duckduckgo(args.query, args.limit)

    if not results:
        print("No results found.", file=sys.stderr)
        sys.exit(1)

    # Output results
    if args.json:
        import json
        output = json.dumps(results, indent=2)
    elif args.output:
        output = format_markdown(results, args.query)
    else:
        # Simple text output
        lines = [f"Search Results for: {args.query}\n"]
        for i, result in enumerate(results, 1):
            lines.append(f"{i}. {result['title']}")
            lines.append(f"   URL: {result['url']}")
            if result['snippet']:
                snippet = result['snippet'][:150] + "..." if len(result['snippet']) > 150 else result['snippet']
                lines.append(f"   {snippet}")
            lines.append("")
        output = "\n".join(lines)

    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results saved to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
