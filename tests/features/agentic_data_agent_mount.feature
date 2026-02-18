# BDD Feature: Agentic data agent mount
# Run via: pytest tests/test_agentic_data_agent_mount_tdd_bdd.py -v

Feature: Agentic data agent mount
  As a developer building an agentic data agent
  I want client/doc to mount client databases with BIRD-style question-SQL pairs
  So that I can develop and evaluate text-to-SQL agents

  Background:
    Given client/db/db-1..db-16 exist
    And each has DOCUMENTATION/README.md and QUERIES/queries.json

  Scenario: Client doc folder structure
    Given client/doc exists
    When README.md is read
    Then it describes agentic data agent and BIRD benchmark alignment
    And it references agentic_data_agent_mount.ipynb

  Scenario: Mount loads documentation and queries
    Given load_client_db is called for db-2
    When the result is inspected
    Then docs is not None
    And queries has 30 items
    And each query has question and sql

  Scenario: BIRD-style pairs available
    Given get_bird_pairs is called for db-2
    When the result is inspected
    Then each pair has question, sql, description, expected_output
    And pairs can be used for agentic training data
