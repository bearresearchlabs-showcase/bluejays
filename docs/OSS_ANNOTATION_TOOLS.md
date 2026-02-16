# OSS Annotation Tools Integration

This document describes supported open-source annotation tools and their integration with the Data Engine platform.

## Supported Tools

| Use Case | Tool | License | Integration |
|----------|------|---------|-------------|
| Multi-modal / Text | [Label Studio](https://github.com/heartexlabs/label-studio) | Apache-2 | `label_studio_adapter.py`, `export_queries_to_label_studio.py` |
| Text | [doccano](https://github.com/doccano/doccano) | MIT | `GET /api/export?format=doccano` |
| Text / NLP | [refinery](https://github.com/code-kern-ai/refinery) | Apache-2 | Documented as alternative for NLP labeling |

## Label Studio

- **Setup**: [Label Studio](https://labelstud.io/guide/start.html)
- **Integration**: Use `db_check label-studio` to export queries for 16 DBs × 30 queries
- **Scripts**: `label_studio_adapter.py`, `export_queries_to_label_studio.py`

## doccano

- **Setup**: [doccano GitHub](https://github.com/doccano/doccano)
- **Export**: `GET /api/export?source=db-1&format=doccano`
- **Format**: JSONL (one JSON object per line) for text classification
- **Schema**: `{"text": "Query N\\nquestion\\nsql snippet", "label": ["audit_status"]}`

## refinery

- **Setup**: [refinery](https://github.com/code-kern-ai/refinery)
- **Use case**: NLP labeling, sequence labeling, document classification
- **Integration**: Document as alternative; export formats may be adapted
