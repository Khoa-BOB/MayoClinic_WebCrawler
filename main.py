from bs4 import BeautifulSoup, NavigableString
import requests
import yaml


class MayoClinicCrawler:
    """Crawls website and extract content"""
    def __init__(self, base_url='https://www.mayoclinic.org/',headers=None):
        self.base_url = base_url
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}
    
    def fetch(self,path):
        """Fetch HTML content from MayoClinic page"""
        url = self.base_url + path
        response = requests.get(url=url,headers=self.headers, timeout=20)
        response.raise_for_status()
        return response.text
    
    def parse(self,html):
        """Parse HTML using BeautifulSoup and lxml parser"""
        soup = BeautifulSoup(html, "lxml")
        return soup

    
    def extract_content(self,soup):
        """Extract content"""
        # Prefer the main article; fall back to any <article>
        article = soup.select_one("article#main-content") or soup.find("article") or soup

        # Title and pubdate (if present)
        title = (soup.find("h1").get_text(" ", strip=True)
                 if soup.find("h1") else None)
        pubdate_el = soup.select_one(".pubdate")
        pubdate = pubdate_el.get_text(" ", strip=True) if pubdate_el else None

        # Build nested heading tree (H2 -> H3 -> H4)
        HEAD_LEVEL = {"h2": 2, "h3": 3, "h4": 4}
        BLOCK_TAGS = {"p", "ul", "ol"}
        root = {"title": title, "pubdate": pubdate, "sections": []}
        stack = [(1, root)]  # (level_number, node_dict)

        for el in article.descendants:
            if isinstance(el, NavigableString) or not getattr(el, "name", None):
                continue
            name = el.name.lower()
            if name in HEAD_LEVEL:
                level = HEAD_LEVEL[name]
                node = {
                    "heading": el.get_text(" ", strip=True),
                    "level": level,
                    "sections": []
                }
                # attach to the nearest parent with lower level
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack[-1][1]["sections"].append(node)
                stack.append((level, node))

            if name in BLOCK_TAGS:
                if name == "p":
                    text = el.get_text(" ", strip=True)
                    if text:
                        # Add paragraph text under the most recent heading
                        stack[-1][1].setdefault("paragraphs", []).append(text)
                elif name in ("ul", "ol"):
                    items = [li.get_text(" ", strip=True) for li in el.find_all("li", recursive=False)]
                    if items:
                        # Add list items under the most recent heading
                        stack[-1][1].setdefault("lists", []).append(items)


        return root

    def crawl(self,path):
        html = self.fetch(path)
        soup = BeautifulSoup(html, "lxml")
        return self.extract_content(soup)

    def export_to_yaml(self, data, output_path):
        """Export crawled data to YAML file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"Data exported to {output_path}")

crawler = MayoClinicCrawler()
data = crawler.crawl("/diseases-conditions/viral-hemorrhagic-fevers/symptoms-causes/syc-20351260?p=1")
print(data)

# Export to YAML
crawler.export_to_yaml(data, "viral-hemorrhagic-fevers.yaml")