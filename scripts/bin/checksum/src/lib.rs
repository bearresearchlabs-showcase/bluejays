//! Library for computing CRC-32, CRC-64-ECMA, SHA-256.
//! Used by main binary and unit tests.

use crc::{Crc, CRC_32_ISO_HDLC};
use sha2::{Digest, Sha256};

/// CRC-64-ECMA polynomial (matches Python crcmod / integrity_checks.py)
const CRC64_ECMA_POLY: u64 = 0xC96C5795D7870F42;

fn crc64_ecma(data: &[u8]) -> u64 {
    let mut table = [0u64; 256];
    for i in 0..256 {
        let mut crc = i as u64;
        for _ in 0..8 {
            if crc & 1 != 0 {
                crc = (crc >> 1) ^ CRC64_ECMA_POLY;
            } else {
                crc >>= 1;
            }
        }
        table[i] = crc;
    }
    let mut crc: u64 = 0;
    for &b in data {
        crc = table[((crc ^ b as u64) & 0xFF) as usize] ^ (crc >> 8);
    }
    crc
}

/// Compute CRC-32, CRC-64-ECMA, SHA-256 for data.
/// Returns JSON string: {"crc32":"0x...","crc64":"0x...","sha256":"..."}
pub fn compute_checksums(data: &[u8]) -> String {
    let crc32 = Crc::<u32>::new(&CRC_32_ISO_HDLC);
    let c32 = crc32.checksum(data);
    let c64 = crc64_ecma(data);
    let mut hasher = Sha256::new();
    hasher.update(data);
    let sha = hasher.finalize();
    let sha_hex: String = sha.iter().map(|b| format!("{:02x}", b)).collect();
    format!(
        r#"{{"crc32":"0x{:08x}","crc64":"0x{:016x}","sha256":"{}"}}"#,
        c32, c64, sha_hex
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_input() {
        let json = compute_checksums(b"");
        let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
        assert!(parsed.get("crc32").is_some());
        assert!(parsed.get("crc64").is_some());
        assert!(parsed.get("sha256").is_some());
        assert_eq!(parsed["sha256"].as_str().unwrap().len(), 64);
    }

    #[test]
    fn test_known_input() {
        // b"test" - matches Python integrity_checks output
        let data = b"test";
        let json = compute_checksums(data);
        let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed["crc32"].as_str().unwrap(), "0xd87f7e0c");
        assert_eq!(parsed["crc64"].as_str().unwrap(), "0x0eb07b92df17eaee");
        assert_eq!(
            parsed["sha256"].as_str().unwrap(),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        );
    }

    #[test]
    fn test_json_format() {
        let json = compute_checksums(b"hello");
        assert!(json.starts_with(r#"{"crc32":"0x"#));
        assert!(json.contains(r#","crc64":"0x"#));
        assert!(json.contains(r#","sha256":"#));
        assert!(json.ends_with('}'));
    }
}
