#!/usr/bin/env python3
"""
Generate individual Jupyter notebooks for each database with query testing, documentation, and visualizations
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DATABASES = [f'db-{i}' for i in range(6, 16)]
NOTEBOOKS_DIR = BASE_DIR / 'notebooks'

def generate_notebook_content(db_name: str, db_dir: Path) -> dict:
    """Generate notebook content for a database."""
    
    # Load queries.json to get database info
    queries_file = db_dir / 'queries' / 'queries.json'
    if not queries_file.exists():
        return None
    
    with open(queries_file) as f:
        queries_data = json.load(f)
    
    total_queries = len(queries_data.get('queries', []))
    db_num = db_name.replace('db-', 'db')
    
    # Determine database domain from first query or directory name
    first_query = queries_data.get('queries', [{}])[0]
    domain_hint = first_query.get('title', '').lower()
    
    if 'weather' in domain_hint or 'forecast' in domain_hint:
        domain = "Weather Forecasting & Insurance"
    elif 'maritime' in domain_hint or 'vessel' in domain_hint or 'shipping' in domain_hint:
        domain = "Maritime Shipping Intelligence"
    elif 'job' in domain_hint or 'career' in domain_hint:
        domain = "Job Market Intelligence"
    elif 'parking' in domain_hint:
        domain = "Parking Intelligence"
    elif 'credit' in domain_hint or 'card' in domain_hint:
        domain = "Credit Card Optimization"
    elif 'retail' in domain_hint or 'price' in domain_hint:
        domain = "Retail Price Intelligence"
    elif 'ai' in domain_hint or 'model' in domain_hint:
        domain = "AI Model Performance"
    elif 'cloud' in domain_hint or 'compute' in domain_hint:
        domain = "Cloud Cost Optimization"
    elif 'electricity' in domain_hint or 'energy' in domain_hint:
        domain = "Energy Rate Optimization"
    else:
        domain = "Data Analytics"
    
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {db_name.upper()}: {domain} Database - Query Testing & Documentation\n",
                    "\n",
                    "This notebook provides comprehensive testing, documentation, and visualization for all SQL queries.\n",
                    "\n",
                    "## Database Overview\n",
                    f"\n",
                    f"**Database Name:** {domain} Database  \n",
                    f"**Database ID:** {db_name}  \n",
                    f"**Domain:** {domain}  \n",
                    f"**Total Queries:** {total_queries}  \n",
                    "\n",
                    "## Workflow\n",
                    "\n",
                    "1. Database initialization (create database, load schema, load data)\n",
                    "2. Query execution and validation\n",
                    "3. Results visualization and analysis\n",
                    "4. Performance metrics and documentation"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Import required libraries\n",
                    "import psycopg2\n",
                    "import json\n",
                    "import os\n",
                    "from pathlib import Path\n",
                    "from datetime import datetime\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "from IPython.display import display, HTML, Markdown\n",
                    "import warnings\n",
                    "warnings.filterwarnings('ignore')\n",
                    "\n",
                    "# Set visualization style\n",
                    "plt.style.use('seaborn-v0_8-darkgrid')\n",
                    "sns.set_palette(\"husl\")\n",
                    "\n",
                    "# Configuration\n",
                    f"DB_NAME = '{db_num}'\n",
                    f"DB_DIR = Path('{db_dir}')\n",
                    "BASE_DIR = Path('/Users/machine/Documents/AQ/db')\n",
                    "\n",
                    "DB_CONFIG = {\n",
                    "    'host': os.getenv('PG_HOST', 'localhost'),\n",
                    "    'port': os.getenv('PG_PORT', '5432'),\n",
                    "    'user': os.getenv('PG_USER', os.getenv('USER', 'machine')),\n",
                    "    'password': os.getenv('PG_PASSWORD', ''),\n",
                    "    'database': 'postgres'\n",
                    "}\n",
                    "\n",
                    "print(f\"Database: {DB_NAME}\")\n",
                    "print(f\"Database Directory: {DB_DIR}\")\n",
                    "print(f\"Configuration: {DB_CONFIG['host']}:{DB_CONFIG['port']}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 1: Database Initialization"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def initialize_database(db_name: str, db_dir: Path, config: dict) -> bool:\n",
                    "    \"\"\"Initialize database: create, load schema, load data.\"\"\"\n",
                    "    try:\n",
                    "        # Connect to postgres database\n",
                    "        conn = psycopg2.connect(**config)\n",
                    "        conn.autocommit = True\n",
                    "        cur = conn.cursor()\n",
                    "        \n",
                    "        # Check if database exists\n",
                    "        cur.execute(\"SELECT 1 FROM pg_database WHERE datname = %s\", (db_name,))\n",
                    "        exists = cur.fetchone()\n",
                    "        \n",
                    "        if not exists:\n",
                    "            cur.execute(f'CREATE DATABASE {db_name}')\n",
                    "            print(f\"✅ Created database: {db_name}\")\n",
                    "        else:\n",
                    "            print(f\"ℹ️  Database {db_name} already exists\")\n",
                    "        \n",
                    "        cur.close()\n",
                    "        conn.close()\n",
                    "        \n",
                    "        # Load schema\n",
                    "        schema_file = db_dir / 'data' / 'schema.sql'\n",
                    "        if schema_file.exists():\n",
                    "            db_config = config.copy()\n",
                    "            db_config['database'] = db_name\n",
                    "            conn = psycopg2.connect(**db_config)\n",
                    "            cur = conn.cursor()\n",
                    "            \n",
                    "            with open(schema_file, 'r') as f:\n",
                    "                schema_sql = f.read()\n",
                    "            \n",
                    "            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]\n",
                    "            for statement in statements:\n",
                    "                if statement:\n",
                    "                    try:\n",
                    "                        cur.execute(statement)\n",
                    "                    except Exception as e:\n",
                    "                        if 'already exists' not in str(e).lower():\n",
                    "                            pass\n",
                    "            \n",
                    "            conn.commit()\n",
                    "            cur.close()\n",
                    "            conn.close()\n",
                    "            print(f\"✅ Loaded schema for {db_name}\")\n",
                    "        \n",
                    "        # Load data\n",
                    "        data_file = db_dir / 'data' / 'data.sql'\n",
                    "        if data_file.exists():\n",
                    "            db_config = config.copy()\n",
                    "            db_config['database'] = db_name\n",
                    "            conn = psycopg2.connect(**db_config)\n",
                    "            cur = conn.cursor()\n",
                    "            \n",
                    "            with open(data_file, 'r') as f:\n",
                    "                data_sql = f.read()\n",
                    "            \n",
                    "            statements = [s.strip() for s in data_sql.split(';') if s.strip()]\n",
                    "            for statement in statements:\n",
                    "                if statement:\n",
                    "                    try:\n",
                    "                        cur.execute(statement)\n",
                    "                    except Exception as e:\n",
                    "                        if 'duplicate' not in str(e).lower():\n",
                    "                            pass\n",
                    "            \n",
                    "            conn.commit()\n",
                    "            cur.close()\n",
                    "            conn.close()\n",
                    "            print(f\"✅ Loaded data for {db_name}\")\n",
                    "        \n",
                    "        return True\n",
                    "    except Exception as e:\n",
                    "        print(f\"❌ Error initializing database: {e}\")\n",
                    "        return False\n",
                    "\n",
                    "# Initialize database\n",
                    "print(\"=\"*60)\n",
                    "print(\"DATABASE INITIALIZATION\")\n",
                    "print(\"=\"*60)\n",
                    "initialize_database(DB_NAME, DB_DIR, DB_CONFIG)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 2: Load Query Metadata"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load queries from JSON\n",
                    "queries_file = DB_DIR / 'queries' / 'queries.json'\n",
                    "\n",
                    "with open(queries_file) as f:\n",
                    "    queries_data = json.load(f)\n",
                    "\n",
                    "queries = queries_data.get('queries', [])\n",
                    "total_queries = len(queries)\n",
                    "\n",
                    "print(f\"Loaded {total_queries} queries from {queries_file}\")\n",
                    "print(f\"\\nQuery Overview:\")\n",
                    "for q in queries[:5]:  # Show first 5\n",
                    "    print(f\"  Query {q.get('number')}: {q.get('title', 'N/A')[:60]}...\")\n",
                    "if total_queries > 5:\n",
                    "    print(f\"  ... and {total_queries - 5} more queries\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 3: Query Execution Function"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def execute_query_with_metrics(db_name: str, query_sql: str, query_num: int, config: dict):\n",
                    "    \"\"\"Execute a query and return results with metrics.\"\"\"\n",
                    "    db_config = config.copy()\n",
                    "    db_config['database'] = db_name\n",
                    "    \n",
                    "    start_time = datetime.now()\n",
                    "    \n",
                    "    try:\n",
                    "        conn = psycopg2.connect(**db_config)\n",
                    "        cur = conn.cursor()\n",
                    "        \n",
                    "        query_clean = query_sql.strip().rstrip(';')\n",
                    "        cur.execute(query_clean)\n",
                    "        \n",
                    "        columns = [desc[0] for desc in cur.description] if cur.description else []\n",
                    "        rows = cur.fetchall()\n",
                    "        \n",
                    "        df = pd.DataFrame(rows, columns=columns) if columns else pd.DataFrame()\n",
                    "        \n",
                    "        execution_time = (datetime.now() - start_time).total_seconds()\n",
                    "        \n",
                    "        cur.close()\n",
                    "        conn.close()\n",
                    "        \n",
                    "        return {\n",
                    "            'success': True,\n",
                    "            'error': None,\n",
                    "            'dataframe': df,\n",
                    "            'execution_time': execution_time,\n",
                    "            'row_count': len(df),\n",
                    "            'column_count': len(df.columns),\n",
                    "            'columns': columns\n",
                    "        }\n",
                    "        \n",
                    "    except Exception as e:\n",
                    "        execution_time = (datetime.now() - start_time).total_seconds()\n",
                    "        error_msg = str(e)\n",
                    "        \n",
                    "        if 'cur' in locals():\n",
                    "            cur.close()\n",
                    "        if 'conn' in locals():\n",
                    "            conn.close()\n",
                    "        \n",
                    "        return {\n",
                    "            'success': False,\n",
                    "            'error': error_msg,\n",
                    "            'dataframe': None,\n",
                    "            'execution_time': execution_time,\n",
                    "            'row_count': 0,\n",
                    "            'column_count': 0,\n",
                    "            'columns': []\n",
                    "        }"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 4: Execute All Queries"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Execute all queries and collect results\n",
                    "all_results = []\n",
                    "\n",
                    "print(\"=\"*60)\n",
                    "print(\"EXECUTING ALL QUERIES\")\n",
                    "print(\"=\"*60)\n",
                    "\n",
                    "for query_info in queries:\n",
                    "    query_num = query_info.get('number')\n",
                    "    query_sql = query_info.get('sql', '')\n",
                    "    query_title = query_info.get('title', f'Query {query_num}')\n",
                    "    \n",
                    "    result = execute_query_with_metrics(DB_NAME, query_sql, query_num, DB_CONFIG)\n",
                    "    result['query_number'] = query_num\n",
                    "    result['query_title'] = query_title\n",
                    "    result['query_info'] = query_info\n",
                    "    \n",
                    "    all_results.append(result)\n",
                    "    \n",
                    "    status = \"✅\" if result['success'] else \"❌\"\n",
                    "    print(f\"{status} Query {query_num}: {query_title[:50]}... ({result['execution_time']:.3f}s, {result['row_count']} rows)\")\n",
                    "\n",
                    "# Summary\n",
                    "passed = sum(1 for r in all_results if r['success'])\n",
                    "failed = sum(1 for r in all_results if not r['success'])\n",
                    "print(f\"\\n{'='*60}\")\n",
                    "print(f\"SUMMARY: {passed}/{total_queries} passed ({passed/total_queries*100:.1f}%)\")\n",
                    "print(f\"{'='*60}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 5: Performance Visualization"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Create performance metrics DataFrame\n",
                    "perf_data = []\n",
                    "for r in all_results:\n",
                    "    perf_data.append({\n",
                    "        'Query': r['query_number'],\n",
                    "        'Title': r['query_title'][:40] + '...' if len(r['query_title']) > 40 else r['query_title'],\n",
                    "        'Execution Time (s)': r['execution_time'],\n",
                    "        'Row Count': r['row_count'],\n",
                    "        'Column Count': r['column_count'],\n",
                    "        'Status': 'Passed' if r['success'] else 'Failed'\n",
                    "    })\n",
                    "\n",
                    "perf_df = pd.DataFrame(perf_data)\n",
                    "\n",
                    "# Visualization 1: Execution Time Distribution\n",
                    "fig, axes = plt.subplots(2, 2, figsize=(15, 12))\n",
                    "\n",
                    "# Execution time bar chart\n",
                    "axes[0, 0].bar(perf_df['Query'], perf_df['Execution Time (s)'], color='steelblue', alpha=0.7)\n",
                    "axes[0, 0].set_xlabel('Query Number')\n",
                    "axes[0, 0].set_ylabel('Execution Time (seconds)')\n",
                    "axes[0, 0].set_title('Query Execution Time by Query Number')\n",
                    "axes[0, 0].tick_params(axis='x', rotation=45)\n",
                    "axes[0, 0].grid(True, alpha=0.3)\n",
                    "\n",
                    "# Execution time histogram\n",
                    "axes[0, 1].hist(perf_df['Execution Time (s)'], bins=20, color='coral', alpha=0.7, edgecolor='black')\n",
                    "axes[0, 1].set_xlabel('Execution Time (seconds)')\n",
                    "axes[0, 1].set_ylabel('Frequency')\n",
                    "axes[0, 1].set_title('Distribution of Execution Times')\n",
                    "axes[0, 1].grid(True, alpha=0.3)\n",
                    "\n",
                    "# Row count bar chart\n",
                    "axes[1, 0].bar(perf_df['Query'], perf_df['Row Count'], color='green', alpha=0.7)\n",
                    "axes[1, 0].set_xlabel('Query Number')\n",
                    "axes[1, 0].set_ylabel('Row Count')\n",
                    "axes[1, 0].set_title('Rows Returned by Query')\n",
                    "axes[1, 0].tick_params(axis='x', rotation=45)\n",
                    "axes[1, 0].grid(True, alpha=0.3)\n",
                    "\n",
                    "# Status pie chart\n",
                    "status_counts = perf_df['Status'].value_counts()\n",
                    "axes[1, 1].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', startangle=90)\n",
                    "axes[1, 1].set_title('Query Execution Status')\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()\n",
                    "\n",
                    "# Display performance summary table\n",
                    "print(\"\\nPerformance Summary:\")\n",
                    "print(f\"  Average execution time: {perf_df['Execution Time (s)'].mean():.3f}s\")\n",
                    "print(f\"  Median execution time: {perf_df['Execution Time (s)'].median():.3f}s\")\n",
                    "print(f\"  Max execution time: {perf_df['Execution Time (s)'].max():.3f}s\")\n",
                    "print(f\"  Min execution time: {perf_df['Execution Time (s)'].min():.3f}s\")\n",
                    "print(f\"  Total rows returned: {perf_df['Row Count'].sum():,}\")\n",
                    "print(f\"  Average rows per query: {perf_df['Row Count'].mean():.1f}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 6: Individual Query Documentation and Visualization"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def document_and_visualize_query(query_result: dict, query_num: int):\n",
                    "    \"\"\"Create comprehensive documentation and visualization for a single query.\"\"\"\n",
                    "    query_info = query_result['query_info']\n",
                    "    \n",
                    "    # Create markdown documentation\n",
                    "    doc = f\"\"\"\n",
                    "## Query {query_num}: {query_info.get('title', 'N/A')}\n",
                    "\n",
                    "### Execution Status\n",
                    "- **Status:** {'✅ PASSED' if query_result['success'] else '❌ FAILED'}\n",
                    "- **Execution Time:** {query_result['execution_time']:.3f} seconds\n",
                    "- **Rows Returned:** {query_result['row_count']:,}\n",
                    "- **Columns Returned:** {query_result['column_count']}\n",
                    "\n",
                    "### Query Information\n",
                    "- **Description:** {query_info.get('description', 'N/A')[:300]}...\n",
                    "- **Use Case:** {query_info.get('use_case', 'N/A')}\n",
                    "- **Business Value:** {query_info.get('business_value', 'N/A')}\n",
                    "- **Complexity:** {query_info.get('complexity', 'N/A')}\n",
                    "- **Expected Output:** {query_info.get('expected_output', 'N/A')}\n",
                    "\n",
                    "### SQL Query\n",
                    "```sql\n",
                    "{query_info.get('sql', '')[:1000]}...\n",
                    "```\n",
                    "\n",
                    "### Results Preview\n",
                    "\"\"\"\n",
                    "    \n",
                    "    display(Markdown(doc))\n",
                    "    \n",
                    "    if query_result['success'] and query_result['dataframe'] is not None:\n",
                    "        df = query_result['dataframe']\n",
                    "        \n",
                    "        if len(df) > 0:\n",
                    "            print(f\"\\nFirst 10 rows of Query {query_num}:\")\n",
                    "            display(df.head(10))\n",
                    "            \n",
                    "            # Create visualizations if numeric data exists\n",
                    "            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()\n",
                    "            if len(numeric_cols) > 0:\n",
                    "                num_plots = min(3, len(numeric_cols))\n",
                    "                fig, axes = plt.subplots(1, num_plots, figsize=(15, 4))\n",
                    "                if num_plots == 1:\n",
                    "                    axes = [axes]\n",
                    "                \n",
                    "                for idx, col in enumerate(numeric_cols[:num_plots]):\n",
                    "                    if df[col].notna().sum() > 0:\n",
                    "                        axes[idx].hist(df[col].dropna(), bins=min(20, len(df)), alpha=0.7, edgecolor='black')\n",
                    "                        axes[idx].set_title(f'Distribution of {col[:30]}')\n",
                    "                        axes[idx].set_xlabel(col[:30])\n",
                    "                        axes[idx].set_ylabel('Frequency')\n",
                    "                        axes[idx].grid(True, alpha=0.3)\n",
                    "                \n",
                    "                plt.tight_layout()\n",
                    "                plt.show()\n",
                    "                \n",
                    "                # Create correlation heatmap if multiple numeric columns\n",
                    "                if len(numeric_cols) > 1:\n",
                    "                    fig, ax = plt.subplots(figsize=(10, 8))\n",
                    "                    corr_matrix = df[numeric_cols].corr()\n",
                    "                    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)\n",
                    "                    ax.set_title('Correlation Matrix of Numeric Columns')\n",
                    "                    plt.tight_layout()\n",
                    "                    plt.show()\n",
                    "        else:\n",
                    "            print(f\"\\nQuery {query_num} returned 0 rows.\")\n",
                    "    else:\n",
                    "        if query_result.get('error'):\n",
                    "            print(f\"\\n❌ Error: {query_result['error'][:200]}\")\n",
                    "\n",
                    "# Document and visualize each query\n",
                    "for query_result in all_results:\n",
                    "    query_num = query_result['query_number']\n",
                    "    document_and_visualize_query(query_result, query_num)\n",
                    "    print(\"\\n\" + \"=\"*80 + \"\\n\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Step 7: Generate Comprehensive Report"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Create comprehensive report\n",
                    "report_data = {\n",
                    "    'database': DB_NAME,\n",
                    "    'test_timestamp': datetime.now().isoformat(),\n",
                    "    'total_queries': total_queries,\n",
                    "    'passed': passed,\n",
                    "    'failed': failed,\n",
                    "    'success_rate': passed / total_queries * 100,\n",
                    "    'average_execution_time': perf_df['Execution Time (s)'].mean(),\n",
                    "    'total_execution_time': perf_df['Execution Time (s)'].sum(),\n",
                    "    'queries': []\n",
                    "}\n",
                    "\n",
                    "for r in all_results:\n",
                    "    query_report = {\n",
                    "        'number': r['query_number'],\n",
                    "        'title': r['query_title'],\n",
                    "        'success': r['success'],\n",
                    "        'execution_time': r['execution_time'],\n",
                    "        'row_count': r['row_count'],\n",
                    "        'column_count': r['column_count'],\n",
                    "        'columns': r['columns']\n",
                    "    }\n",
                    "    if not r['success']:\n",
                    "        query_report['error'] = r['error']\n",
                    "    \n",
                    "    report_data['queries'].append(query_report)\n",
                    "\n",
                    "# Save report\n",
                    "report_file = DB_DIR / 'results' / f'{DB_NAME}_comprehensive_report.json'\n",
                    "report_file.parent.mkdir(exist_ok=True)\n",
                    "\n",
                    "with open(report_file, 'w') as f:\n",
                    "    json.dump(report_data, f, indent=2, default=str)\n",
                    "\n",
                    "print(f\"✅ Comprehensive report saved to: {report_file}\")\n",
                    "\n",
                    "# Display summary\n",
                    "print(\"\\n\" + \"=\"*60)\n",
                    "print(\"COMPREHENSIVE TEST REPORT\")\n",
                    "print(\"=\"*60)\n",
                    "print(f\"Database: {DB_NAME}\")\n",
                    "print(f\"Total Queries: {total_queries}\")\n",
                    "print(f\"Passed: {passed}\")\n",
                    "print(f\"Failed: {failed}\")\n",
                    "print(f\"Success Rate: {passed/total_queries*100:.1f}%\")\n",
                    "print(f\"Average Execution Time: {perf_df['Execution Time (s)'].mean():.3f}s\")\n",
                    "print(f\"Total Execution Time: {perf_df['Execution Time (s)'].sum():.3f}s\")"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.9.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    return notebook

def main():
    """Generate notebooks for all databases."""
    NOTEBOOKS_DIR.mkdir(exist_ok=True)
    
    print("="*60)
    print("GENERATING QUERY TESTING NOTEBOOKS")
    print("="*60)
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        
        if not db_dir.exists():
            print(f"⚠️  Skipping {db_name} - directory not found")
            continue
        
        print(f"\\nGenerating notebook for {db_name}...")
        
        notebook_content = generate_notebook_content(db_name, db_dir)
        
        if notebook_content:
            notebook_file = NOTEBOOKS_DIR / f'{db_name}_query_testing.ipynb'
            
            with open(notebook_file, 'w') as f:
                json.dump(notebook_content, f, indent=1)
            
            print(f"✅ Created: {notebook_file}")
        else:
            print(f"❌ Failed to generate notebook for {db_name}")
    
    print(f"\\n{'='*60}")
    print(f"Generated {len(DATABASES)} notebooks in {NOTEBOOKS_DIR}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
