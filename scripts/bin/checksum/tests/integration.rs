//! Integration tests: run checksum binary and verify output.
//! Run: cargo build --release && cargo test --release --test integration
use std::process::Command;
use std::path::PathBuf;

fn checksum_bin() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("target")
        .join("release")
        .join("checksum")
}

#[test]
fn test_checksum_binary_output_format() {
    let bin = checksum_bin();
    if !bin.exists() {
        eprintln!("Skipping: run 'cargo build --release' first");
        return;
    }
    let tmp = std::env::temp_dir().join("checksum_test_integration.txt");
    std::fs::write(&tmp, b"hello").unwrap();
    let out = Command::new(&bin)
        .arg(&tmp)
        .output()
        .expect("run checksum");
    std::fs::remove_file(&tmp).ok();
    assert!(out.status.success(), "checksum should succeed: {:?}", out.stderr);
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("\"crc32\""), "output should contain crc32");
    assert!(stdout.contains("\"crc64\""), "output should contain crc64");
    assert!(stdout.contains("\"sha256\""), "output should contain sha256");
}
