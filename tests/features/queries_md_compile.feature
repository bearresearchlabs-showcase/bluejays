# BDD Feature: queries.md Compilation and Formatting
# Run via: pytest tests/test_queries_md_compile_tdd_bdd.py -v

Feature: queries.md compilation and consistency
  As a developer
  I want queries.md to be compiled correctly from queries.json and header
  So that formatting is consistent and data stays in sync

  Background:
    Given the source database "db-1" exists
    And queries.json exists in app/QUERIES or queries/

  Scenario: Compilation produces valid structure
    Given queries.json has at least 30 queries
    And queries_header.yaml exists at source/db-N/ (optional)
    When rewrite_queries_md_to_template runs for db-1
    Then queries.md contains "## Database Overview"
    And queries.md contains "## Purpose"
    And queries.md contains "## Use Case"
    And queries.md contains "## Business Value"
    And queries.md contains "## Schema"
    And queries.md contains "## Domain Knowledge"
    And queries.md contains "## Query Difficulty Distribution"
    And queries.md contains "## Queries"
    And queries.md has at least 30 "### Query N — " blocks
    And each JSON block is valid JSON with SQL and question_id

  Scenario: Headers follow HTML-like hierarchy
    Given queries.md exists
    When headers are parsed
    Then there is exactly one h1 (title with em dash)
    And h2 sections appear in canonical order
    And h3 (Query N) headers match "Query N — difficulty / category"
    And no h3 appears before "## Queries"

  Scenario: Data update from JSON
    Given queries.md and queries.json exist
    When update_queries_md_from_json runs with modified evidence/SQL
    Then queries.md reflects the new evidence
    And queries.md reflects the new SQL
    And header sections remain intact
