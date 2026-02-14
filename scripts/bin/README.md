# Compiled Binaries

Single-purpose programs for consistent, fast behavior. No Python runtime required.

## checksum

Computes CRC-32, CRC-64-ECMA, SHA-256 for a file. Output: JSON.

```bash
# Build
make -C scripts/bin checksum
# or: cd scripts/bin/checksum && cargo build --release

# Run
./scripts/bin/checksum/target/release/checksum <file>
# Output: {"crc32":"0x...","crc64":"0x...","sha256":"..."}
```

**Used by:** `integrity_checks.py` (uses binary when built, else Python fallback)

**Requirements:** Rust toolchain (`rustc`, `cargo`)

### Tests

```bash
# Rust unit + integration
cd scripts/bin/checksum && cargo test
cargo build --release && cargo test --release --test integration

# Python (includes parity test when binary built)
pytest tests/test_scripts_refactor.py -v
```
