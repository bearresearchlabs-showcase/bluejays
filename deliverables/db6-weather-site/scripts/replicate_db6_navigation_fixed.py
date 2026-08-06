#!/usr/bin/env python3
"""
Replicate db-6's navigation structure for db-7 through db-15
Keeps database names unchanged but populates navigation with same structure
"""

import re
from pathlib import Path

def generate_navigation_template(db_num):
    """Generate navigation structure matching db-6 for a given database number"""
    db_prefix = f"db{db_num}"
    
    # Overview links (same as db-6)
    overview_links = '''                        <a href="#{db_prefix}-overview" class="nav-link">Overview</a>
                        <a href="#{db_prefix}-schema" class="nav-link">Schema</a>
                        <a href="#{db_prefix}-queries" class="nav-link">Queries</a>'''.format(db_prefix=db_prefix)
    
    # Schema links - use db-6's table structure (same table names)
    schema_links = '''                        <a href="#{db_prefix}-table-us_wide_composite_products" class="nav-link">us_wide_composite_products</a>
                        <a href="#{db_prefix}-table-grib2_forecasts" class="nav-link">grib2_forecasts</a>
                        <a href="#{db_prefix}-table-weather_forecast_aggregations" class="nav-link">weather_forecast_aggregations</a>
                        <a href="#{db_prefix}-table-weather_observations" class="nav-link">weather_observations</a>
                        <a href="#{db_prefix}-table-weather_stations" class="nav-link">weather_stations</a>
                        <a href="#{db_prefix}-table-aws_data_source_log" class="nav-link">aws_data_source_log</a>
                        <a href="#{db_prefix}-table-crs_transformation_parameters" class="nav-link">crs_transformation_parameters</a>
                        <a href="#{db_prefix}-table-data_quality_metrics" class="nav-link">data_quality_metrics</a>
                        <a href="#{db_prefix}-table-geoplatform_dataset_log" class="nav-link">geoplatform_dataset_log</a>
                        <a href="#{db_prefix}-table-grib2_transformation_log" class="nav-link">grib2_transformation_log</a>
                        <a href="#{db_prefix}-table-nexrad_transformation_log" class="nav-link">nexrad_transformation_log</a>
                        <a href="#{db_prefix}-table-nws_api_observation_log" class="nav-link">nws_api_observation_log</a>
                        <a href="#{db_prefix}-table-satellite_transformation_log" class="nav-link">satellite_transformation_log</a>
                        <a href="#{db_prefix}-table-shapefile_integration_log" class="nav-link">shapefile_integration_log</a>
                        <a href="#{db_prefix}-table-load_status" class="nav-link">load_status</a>'''.format(db_prefix=db_prefix)
    
    # Query links - Query 1 through Query 30 (same as db-6)
    query_links = '\n'.join([f'                        <a href="#{db_prefix}-query-{i}" class="nav-link">Query {i}</a>' for i in range(1, 31)])
    
    navigation = f'''                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="{db_prefix}-overview">
                        <span>Overview</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="{db_prefix}-overview-content">
{overview_links}
                    </div>
                </div>
                
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="{db_prefix}-schema">
                        <span>Schema</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="{db_prefix}-schema-content">
{schema_links}
                    </div>
                </div>
                
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="{db_prefix}-queries">
                        <span>Queries</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="{db_prefix}-queries-content">
{query_links}
                    </div>
                </div>'''
    
    return navigation

def update_navigation_for_all_databases():
    """Update navigation for db-7 through db-15 with db-6's structure"""
    root_dir = Path(__file__).parent.parent
    
    html_file = root_dir / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    if not html_file.exists():
        print(f"❌ Error: {html_file} not found")
        return False
    
    print(f"📖 Reading HTML file...")
    html_content = html_file.read_text(encoding='utf-8')
    
    # Update each database from db-7 to db-15
    for db_num in range(7, 16):
        db_prefix = f"db{db_num}"
        print(f"🔄 Updating {db_prefix} navigation...")
        
        # Find the entire nav-accordion-content section for this database
        # Pattern: from opening nav-accordion-content to closing </div> (3 levels deep)
        pattern = rf'(<div class="nav-accordion-content" id="{db_prefix}-content">)(.*?)(</div>\s*</div>\s*</div>\s*</div>)'
        
        # Generate new navigation content
        new_nav_content = generate_navigation_template(db_num)
        
        # Replace the entire content section
        replacement = rf'\1\n{new_nav_content}\n            \3'
        
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    # Clean up any duplicate closing tags that might have been created
    html_content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', '</div>\n        </div>', html_content)
    
    # Write updated HTML
    print(f"💾 Writing updated HTML...")
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Updated navigation for db-7 through db-15")
    return True

if __name__ == '__main__':
    update_navigation_for_all_databases()
