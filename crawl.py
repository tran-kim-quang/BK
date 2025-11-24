import requests
from bs4 import BeautifulSoup
import os
import re
import time
import random
from urllib.parse import urljoin
from markdownify import markdownify as md

# --- CẤU HÌNH ---
start_url = "https://bkacad.com/khoa-hoc-va-chuyen-nganh.html"
base_domain = "https://bkacad.com"
output_folder = "data_khoa_hoc_bkacad"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_title(text):
    if not text: return "untitled"
    clean_text = re.sub(r'[\\/*?:"<>|]', "_", text)
    clean_text = re.sub(r'[\x00-\x1f]', '', clean_text)
    return clean_text[:80].strip()
def get_content(link):
    try:
        time.sleep(random.uniform(0.5, 1.5))
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        target_div = soup.find('div', class_='course_detail')
        if not target_div:
            target_div = soup.find('div', class_='contents-course')
            
        if target_div:
            html_content = target_div.decode_contents()
            markdown_text = md(html_content, heading_style="ATX", strip=['script', 'style'])
            markdown_text = re.sub(r'\n\s*\n', '\n\n', markdown_text)            
            return markdown_text
        return None

    except Exception as e:
        print(f"{e}")
        return None

def save_to_markdown_file(title, url, content):
    title = clean_title(title)
    filename = f"{title}.md"
    filepath = os.path.join(output_folder, filename)

    file_content = f"""---
title: "{title}"
url: "{url}"
source: "BKACAD Website"
crawled_at: "{time.strftime('%Y-%m-%d')}"
---

# {title}

{content}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    return filename

def main():
    
    current_url = start_url
    page_count = 1
    total_files = 0
    
    while current_url:
        print(f"\nProcessing {page_count}: {current_url}")
        
        try:
            response = requests.get(current_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            course_headers = soup.find_all('h3', class_='c-name')
            
            for header in course_headers:
                link_tag = header.find('a')
                if link_tag:
                    title = link_tag.get('title') or link_tag.get_text(strip=True)
                    raw_link = link_tag.get('href')
                    full_link = urljoin(base_domain, raw_link)
                    
                    print(f"   Writing: {title}...", end='\r')

                    content_md = get_content(full_link)
                    
                    if content_md:
                        save_to_markdown_file(title, full_link, content_md)
                        total_files += 1
            
            print(f"Done page {page_count}.                   ")

            # Switch page
            next_page_tag = soup.find('a', class_='next-page')
            if next_page_tag:
                current_url = urljoin(base_domain, next_page_tag.get('href'))
                page_count += 1
            else:
                current_url = None

        except Exception as e:
            print(f"Error at {page_count}: {e}")
            break

    print(f"\n--- HOÀN TẤT ---")
    print(f"Saved {total_files} in: {output_folder}")

if __name__ == "__main__":
    main()