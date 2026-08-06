#!/usr/bin/env python3
"""
Fix invalid icon names in Eraser.io code files
Replace invalid icons with valid AWS icons or remove icon property
"""
import re
import sys
from pathlib import Path

# Icon mapping: invalid -> valid AWS icons
ICON_MAP = {
    'user': 'aws-cognito',  # User/identity icon
    'server': 'aws-ec2',  # Server/compute icon
    'cloud': 'aws-cloudfront',  # Cloud/external icon
    'database': 'aws-rds',  # Database icon
    'component': None,  # Remove icon for components
}

def fix_icons(content):
    """Replace invalid icon names with valid ones"""
    # Fix icon: user -> aws-cognito
    content = re.sub(r'\[icon:\s*user\]', '[icon: aws-cognito]', content)
    
    # Fix icon: server -> aws-ec2
    content = re.sub(r'\[icon:\s*server([,\]])', r'[icon: aws-ec2\1', content)
    
    # Fix icon: cloud -> aws-cloudfront
    content = re.sub(r'\[icon:\s*cloud([,\]])', r'[icon: aws-cloudfront\1', content)
    
    # Fix icon: database -> aws-rds
    content = re.sub(r'\[icon:\s*database([,\]])', r'[icon: aws-rds\1', content)
    
    # Remove icon: component (no suitable AWS icon) - remove entire [icon: component] block
    content = re.sub(r'\s*\[icon:\s*component\]', '', content)
    content = re.sub(r',\s*icon:\s*component', '', content)
    content = re.sub(r'icon:\s*component,\s*', '', content)
    
    # Clean up orphaned closing brackets (standalone ] after quoted strings)
    content = re.sub(r'\"\s*\]\s*$', '"', content, flags=re.MULTILINE)
    # Also fix cases where ] appears on same line after quoted string
    content = re.sub(r'\"([^\"]*)\"\s*\]\s*\n', r'"\1"\n', content)
    
    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_icons.py <input_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    fixed = fix_icons(content)
    
    with open(input_file, 'w') as f:
        f.write(fixed)
    
    print(f"Fixed icons in {input_file}")

if __name__ == "__main__":
    main()
