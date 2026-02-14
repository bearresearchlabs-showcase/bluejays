#!/bin/bash
# Serve template app — template/ as root so app/ and queries.json are siblings
cd "$(dirname "$0")/.."
echo "Serving template/ at http://localhost:8765"
echo "  App: http://localhost:8765/app/"
echo "  queries.json: http://localhost:8765/queries.json"
cd template && python3 -m http.server 8765
