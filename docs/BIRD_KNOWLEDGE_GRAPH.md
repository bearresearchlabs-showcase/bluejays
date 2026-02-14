# BIRD Knowledge Graph Integration

Reference: [arXiv 2311.07509](https://arxiv.org/pdf/2311.07509) - A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model's Accuracy for Question Answering on Enterprise SQL Databases.

## Findings

KG + ontology improves accuracy (16% vs 54% without).

## BIRD Workbench Adapter

The `bird_workbench_adapter` bridges BIRD benchmark to tb3_workbench with rigorous checks.
It tests databases for **ACID** (Atomicity, Consistency, Isolation, Durability) and **BASE**
(Basically Available, Soft state, Eventual consistency) properties, validating
industrial-grade enterprise DB behavior.

**tb3_workbench is always available.** CI/CD uses Jenkins; local testing uses the same pipeline.
**ANTHROPIC_API_KEY** from `.env` is used for Anthropic models when multiple sessions run independently.

1. **Gates**: Compliance + integrity (from db_check)
2. **Per-task**: SQL validation (EXPLAIN) + execution
3. **Assertions**: Workbench-style min_accuracy (tb3_workbench.assertions)

```bash
# With DB (full validation + execution)
python scripts/db_check.py bird-workbench db-1
python scripts/db_check.py bird-workbench -a

# Without DB (gates only, --no-execute)
python scripts/db_check.py bird-workbench db-1 --no-execute
```

Report: `bird_export/bird_workbench_report.json`

## Future Work

- OWL ontology for db-6 (insurance) and other domains
- R2RML mappings from schema to ontology
- SPARQL vs SQL comparison script
- Integration with `research/knowledge_graph_benchmark/`
