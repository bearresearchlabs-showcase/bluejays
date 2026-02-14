# Build compiled binaries for single-purpose operations.
# Usage: make -C scripts/bin [checksum]

.PHONY: checksum all clean

checksum:
	cd checksum && cargo build --release
	@echo "Built: scripts/bin/checksum/target/release/checksum"

all: checksum

clean:
	cd checksum && cargo clean 2>/dev/null || true
