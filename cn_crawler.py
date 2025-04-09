#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import concurrent.futures
import threading
from queue import Queue

class WebCrawler:
    def __init__(self, base_url, save_dir, max_depth=4, num_threads=5):
        self.base_url = base_url
        self.save_dir = save_dir
        self.max_depth = max_depth
        self.num_threads = num_threads
        self.visited_urls = set()
        self.visited_lock = threading.Lock()  # Lock for thread safety
        self.url_queue = Queue()
        self.url_queue.put((base_url, 1))  # (url, depth)
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def is_valid_url(self, url):
        """Check if the URL is within the cn/ directory"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Must be from the same domain and within cn/ directory
        return (parsed_url.netloc == urlparse(self.base_url).netloc and 
                path.startswith('/cn/'))
    
    def save_page(self, url, html_content):
        """Save the HTML content to a file"""
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        
        # Create file path based on URL structure
        if path == '' or path == 'cn':
            filename = 'index.html'
            dir_path = self.save_dir
        else:
            parts = path.split('/')
            if len(parts) > 1:  # Has subdirectories
                dir_path = os.path.join(self.save_dir, *parts[:-1])
                filename = parts[-1] + '.html' if not parts[-1].endswith('.html') else parts[-1]
            else:
                dir_path = self.save_dir
                filename = parts[0] + '.html' if not parts[0].endswith('.html') else parts[0]
        
        # Create directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)  # Added exist_ok=True to handle race conditions
        
        # Save the file
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Saved: {file_path}")
    
    def extract_links(self, url, html_content, current_depth):
        """Extract valid links from the HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(url, href)
            
            # Only add URLs that are valid and haven't been visited
            with self.visited_lock:
                if (self.is_valid_url(absolute_url) and 
                    absolute_url not in self.visited_urls and
                    current_depth < self.max_depth):
                    links.append((absolute_url, current_depth + 1))
        
        return links
    
    def process_url(self, url, depth):
        """Process a single URL - for threading"""
        # Skip if already visited or beyond max depth
        with self.visited_lock:
            if url in self.visited_urls or depth > self.max_depth:
                return
            # Mark as visited before processing to prevent duplicates
            self.visited_urls.add(url)
        
        print(f"Crawling: {url} (Depth: {depth})")
        
        try:
            # Add a delay to be considerate to the server
            time.sleep(0.5)  # Reduced delay since we're using multiple threads
            
            # Fetch the page
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Save the page
                self.save_page(url, response.text)
                
                # Extract and add new links to the queue
                new_links = self.extract_links(url, response.text, depth)
                for link, new_depth in new_links:
                    self.url_queue.put((link, new_depth))
            else:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
        
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
    
    def worker(self):
        """Worker function for thread pool"""
        while True:
            try:
                # Get URL from queue with timeout
                url, depth = self.url_queue.get(timeout=5)
                self.process_url(url, depth)
                self.url_queue.task_done()
            except Exception as e:
                # If queue.Empty exception or other error, break the loop
                break
    
    def crawl(self):
        """Start the multithreaded crawling process"""
        # Create and start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for queue to be empty
        self.url_queue.join()
        
        # Add a small delay to allow threads to finish
        time.sleep(2)
        
        print(f"\nCrawling complete. Visited {len(self.visited_urls)} URLs.")
        print(f"Pages saved to: {os.path.abspath(self.save_dir)}")

if __name__ == "__main__":
    base_url = "https://tlidb.com/cn/"
    save_dir = "downloaded_pages"
    num_threads = 8  # Set number of concurrent threads
    
    crawler = WebCrawler(base_url, save_dir, max_depth=4, num_threads=num_threads)
    crawler.crawl()
    
    print("Download complete!") 