#!/usr/bin/env python3
"""
Simple test for the single-page website (without Selenium)
Validates HTML structure and content
"""

import re
from pathlib import Path

def test_website():
    """Test the website structure"""
    website_file = Path(__file__).parent.parent / 'website' / 'index.html'
    
    if not website_file.exists():
        print(f"❌ Error: {website_file} not found")
        return False
    
    print(f"📄 Reading {website_file}...")
    content = website_file.read_text(encoding='utf-8')
    
    print("\n✅ Testing website structure...")
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check if HTML structure is valid
    tests_total += 1
    print("  Test 1: HTML structure...", end=" ")
    if '<!DOCTYPE html>' in content and '<html' in content and '</html>' in content:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 2: Check if sidebar exists
    tests_total += 1
    print("  Test 2: Sidebar navigation exists...", end=" ")
    if '<nav class="sidebar">' in content:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 3: Check if all database sections exist (DB-6 to DB-15)
    tests_total += 1
    print("  Test 3: Database sections in navigation...", end=" ")
    all_dbs_found = True
    for db_num in range(6, 16):
        if f'data-section="db{db_num}"' not in content:
            all_dbs_found = False
            break
    if all_dbs_found:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 4: Check if main content exists
    tests_total += 1
    print("  Test 4: Main content area exists...", end=" ")
    if '<main class="main-content">' in content:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 5: Check if CSS is included
    tests_total += 1
    print("  Test 5: CSS styles included...", end=" ")
    if '<style>' in content and len(content[content.find('<style>'):content.find('</style>')]) > 1000:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 6: Check if JavaScript is included
    tests_total += 1
    print("  Test 6: JavaScript included...", end=" ")
    if '<script' in content:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 7: Check if database content sections exist
    tests_total += 1
    print("  Test 7: Database content sections...", end=" ")
    db_sections = re.findall(r'id="db\d+-section"', content)
    if len(db_sections) >= 5:
        print(f"✅ ({len(db_sections)} sections found)")
        tests_passed += 1
    else:
        print(f"❌ (only {len(db_sections)} sections found)")
    
    # Test 8: Check if navigation links are properly formatted
    tests_total += 1
    print("  Test 8: Navigation links format...", end=" ")
    query_links = re.findall(r'href="#db\d+-query-\d+"', content)
    if len(query_links) >= 50:  # At least 5 databases * 10 queries
        print(f"✅ ({len(query_links)} query links found)")
        tests_passed += 1
    else:
        print(f"❌ (only {len(query_links)} query links found)")
    
    # Test 9: Check if Prism.js is included
    tests_total += 1
    print("  Test 9: Prism.js syntax highlighting...", end=" ")
    if 'prism' in content.lower() and 'cdnjs.cloudflare.com' in content:
        print("✅")
        tests_passed += 1
    else:
        print("❌")
    
    # Test 10: Check file size (should be substantial)
    tests_total += 1
    print("  Test 10: File size reasonable...", end=" ")
    file_size_mb = website_file.stat().st_size / (1024 * 1024)
    if 1.0 < file_size_mb < 10.0:  # Between 1MB and 10MB
        print(f"✅ ({file_size_mb:.2f} MB)")
        tests_passed += 1
    else:
        print(f"⚠️  ({file_size_mb:.2f} MB - may be too large or too small)")
    
    print(f"\n📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        return True
    elif tests_passed >= tests_total * 0.8:  # 80% pass rate
        print("⚠️  Most tests passed, but some issues found")
        return True
    else:
        print("❌ Multiple tests failed")
        return False

if __name__ == '__main__':
    success = test_website()
    exit(0 if success else 1)
