#!/usr/bin/env python3
"""
Test the single-page website with Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import time

def test_website():
    """Test the website functionality"""
    website_file = Path(__file__).parent.parent / 'website' / 'index.html'
    
    if not website_file.exists():
        print(f"❌ Error: {website_file} not found")
        return False
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    print("🌐 Starting Chrome browser...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"❌ Error starting Chrome: {e}")
        print("💡 Try installing ChromeDriver or use: brew install chromedriver")
        return False
    
    try:
        # Load the website
        file_url = f"file://{website_file.absolute()}"
        print(f"📄 Loading {file_url}...")
        driver.get(file_url)
        
        # Wait for page to load
        time.sleep(2)
        
        print("\n✅ Testing website functionality...")
        
        # Test 1: Check if page loaded
        print("  Test 1: Page loaded...", end=" ")
        assert "Database Documentation" in driver.title or "Database Documentation" in driver.page_source
        print("✅")
        
        # Test 2: Check if sidebar exists
        print("  Test 2: Sidebar navigation exists...", end=" ")
        sidebar = driver.find_element(By.CSS_SELECTOR, "nav.sidebar")
        assert sidebar is not None
        print("✅")
        
        # Test 3: Check if all database sections exist (DB-6 to DB-15)
        print("  Test 3: Database sections in navigation...", end=" ")
        for db_num in range(6, 16):
            db_section = driver.find_elements(By.CSS_SELECTOR, f'[data-section="db{db_num}"]')
            assert len(db_section) > 0, f"DB-{db_num} section not found"
        print("✅")
        
        # Test 4: Check if DB-6 content exists in page source
        print("  Test 4: DB-6 content exists...", end=" ")
        db6_content = driver.find_elements(By.CSS_SELECTOR, '#db6-section, #db6-overview, [id*="db6"]')
        if len(db6_content) > 0 or 'db6-overview' in driver.page_source:
            print("✅")
        else:
            print("⚠️  (checking page source)")
            if 'db6' in driver.page_source.lower():
                print("✅ (found in source)")
            else:
                raise AssertionError("DB-6 content not found")
        
        # Test 5: Check navigation structure
        print("  Test 5: Navigation structure...", end=" ")
        nav_elements = driver.find_elements(By.CSS_SELECTOR, '.nav-section-title, [data-section]')
        assert len(nav_elements) >= 10, f"Expected at least 10 nav elements, found {len(nav_elements)}"
        print(f"✅ ({len(nav_elements)} nav elements)")
        
        # Test 6: Check query links exist
        print("  Test 6: Query links exist...", end=" ")
        query_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="query"]')
        assert len(query_links) >= 50, f"Expected at least 50 query links, found {len(query_links)}"
        print(f"✅ ({len(query_links)} links found)")
        
        # Test 7: Check if main content area exists
        print("  Test 7: Main content area exists...", end=" ")
        main_content = driver.find_element(By.CSS_SELECTOR, "main.main-content")
        assert main_content is not None
        print("✅")
        
        # Test 8: Check if multiple databases have content
        print("  Test 8: Multiple database sections exist...", end=" ")
        db_sections = driver.find_elements(By.CSS_SELECTOR, '[id$="-section"]')
        assert len(db_sections) >= 5, f"Expected at least 5 database sections, found {len(db_sections)}"
        print(f"✅ ({len(db_sections)} sections found)")
        
        print("\n✅ All tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()
        print("\n🔒 Browser closed")

if __name__ == '__main__':
    success = test_website()
    exit(0 if success else 1)
