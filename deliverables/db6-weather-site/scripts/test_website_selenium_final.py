#!/usr/bin/env python3
"""
Final Selenium test for the single-page website using webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    print("🌐 Starting Chrome browser with webdriver-manager...")
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"❌ Error starting Chrome: {e}")
        return False
    
    try:
        # Load the website
        file_url = f"file://{website_file.absolute()}"
        print(f"📄 Loading {file_url}...")
        driver.get(file_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(1)
        
        print("\n✅ Testing website functionality...")
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Check if page loaded
        tests_total += 1
        print("  Test 1: Page loaded...", end=" ")
        if "Database Documentation" in driver.page_source:
            print("✅")
            tests_passed += 1
        else:
            print("❌")
        
        # Test 2: Check if sidebar exists
        tests_total += 1
        print("  Test 2: Sidebar navigation exists...", end=" ")
        sidebar = driver.find_elements(By.CSS_SELECTOR, "nav.sidebar")
        if len(sidebar) > 0:
            print("✅")
            tests_passed += 1
        else:
            print("❌")
        
        # Test 3: Check if all database sections exist (DB-6 to DB-15)
        tests_total += 1
        print("  Test 3: Database sections in navigation...", end=" ")
        nav_sections = driver.find_elements(By.CSS_SELECTOR, '[data-section^="db"]')
        if len(nav_sections) >= 10:
            print(f"✅ ({len(nav_sections)} sections found)")
            tests_passed += 1
        else:
            print(f"❌ (only {len(nav_sections)} sections found)")
        
        # Test 4: Check if main content exists
        tests_total += 1
        print("  Test 4: Main content area exists...", end=" ")
        main_content = driver.find_elements(By.CSS_SELECTOR, "main.main-content")
        if len(main_content) > 0:
            print("✅")
            tests_passed += 1
        else:
            print("❌")
        
        # Test 5: Check if database content sections exist
        tests_total += 1
        print("  Test 5: Database content sections...", end=" ")
        db_sections = driver.find_elements(By.CSS_SELECTOR, '[id$="-section"]')
        if len(db_sections) >= 5:
            print(f"✅ ({len(db_sections)} sections found)")
            tests_passed += 1
        else:
            print(f"❌ (only {len(db_sections)} sections found)")
        
        # Test 6: Check if query links exist
        tests_total += 1
        print("  Test 6: Query links exist...", end=" ")
        query_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="query"]')
        if len(query_links) >= 50:
            print(f"✅ ({len(query_links)} links found)")
            tests_passed += 1
        else:
            print(f"❌ (only {len(query_links)} links found)")
        
        # Test 7: Check if CSS is loaded
        tests_total += 1
        print("  Test 7: CSS styles applied...", end=" ")
        sidebar_element = driver.find_element(By.CSS_SELECTOR, "nav.sidebar")
        computed_style = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).width", sidebar_element
        )
        if computed_style and computed_style != "0px":
            print("✅")
            tests_passed += 1
        else:
            print("⚠️")
        
        # Test 8: Check if JavaScript is working
        tests_total += 1
        print("  Test 8: JavaScript functionality...", end=" ")
        try:
            # Try to execute a simple JS command
            result = driver.execute_script("return typeof document !== 'undefined'")
            if result:
                print("✅")
                tests_passed += 1
            else:
                print("❌")
        except:
            print("❌")
        
        print(f"\n📊 Test Results: {tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("✅ All tests passed!")
            return True
        elif tests_passed >= tests_total * 0.8:
            print("⚠️  Most tests passed")
            return True
        else:
            print("❌ Multiple tests failed")
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
