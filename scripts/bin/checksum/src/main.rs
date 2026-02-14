//! db-checksum: Compute CRC-32, CRC-64-ECMA, SHA-256 for a file.
//! Output: JSON {"crc32":"0x...","crc64":"0x...","sha256":"..."}

use db_checksum::compute_checksums;
use std::env;
use std::fs;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: checksum <file>");
        eprintln!("Output: JSON with crc32, crc64, sha256");
        process::exit(1);
    }
    let path = &args[1];
    let data = match fs::read(path) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("Error reading {}: {}", path, e);
            process::exit(1);
        }
    };
    println!("{}", compute_checksums(&data));
}
