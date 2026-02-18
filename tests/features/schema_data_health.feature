# BDD Feature: Schema and Data Validation
# Run via: pytest tests/test_schema_data_validation_tdd_bdd.py -v

Feature: Schema and data validation
  As a developer
  I want schema.sql and data.sql to meet size, PostgreSQL compliance, and naming standards
  So that the repo stays healthy and app/ compiles correctly

  Background:
    Given source/db-1..db-16 exist
    And data.sql or data_large.sql exists per db

  Scenario: Data volume meets 1GB total
    Given source/db-1..db-16 have data.sql or app/DATABASE/data.sql
    When total size is computed
    Then total >= 1GB
    And REPO_HEALTH_LENIENT=1 allows skip during migration

  Scenario: Schema is PostgreSQL compliant
    Given schema.sql exists per db-N
    When validated for PostgreSQL
    Then no incompatible types (TIMESTAMP_NTZ, VARIANT, etc.)
    And CREATE TABLE present

  Scenario: Naming is consistent
    Given schema.sql and data.sql exist
    Then table names use snake_case
    And column names use snake_case
