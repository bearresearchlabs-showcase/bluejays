# BDD Feature: CDC and All-Databases Notebook Runtime
# Run via: pytest tests/test_watch_source_and_sync.py tests/test_all_databases_notebook.py -v

Feature: Change propagation and notebook runtime
  As a developer
  I want file-based and DB-level CDC with a running session notebook
  So that source changes propagate and Docker status is checked

  Background:
    Given source/db-1..db-16 exist
    And Docker PostgreSQL runs on ports 5436-5451 (or is not running)

  Scenario: File-based CDC watches source material
    Given watchdog is installed
    When watch_source_and_sync runs in daemon mode
    Then it watches queries.json, queries_header.yaml, schema.sql, data.sql
    And on change it runs source_material_checks
    And on pass it runs populate_app_trifecta and resync_client_db
    And optionally reloads Docker PostgreSQL

  Scenario: DB-level CDC has wal_level=logical
    Given docker-compose.hardened.yml is used
    When PostgreSQL containers start
    Then each container has wal_level=logical
    And logical replication slots are available for consumers

  Scenario: Notebook checks Docker runtime
    Given all_databases_session.ipynb is opened
    When Setup and Docker Runtime Check cells run
    Then Docker status is checked (docker info)
    And if Docker is not running, a warning is shown
    And PostgreSQL container count is displayed

  Scenario: Notebook source inventory
    Given source/db-N directories exist
    When Source Inventory cell runs
    Then a table shows db, queries_json, header, schema, data, app_populated
    And get_queries_dir and get_data_dir resolve app/ or legacy paths
