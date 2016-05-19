extern crate regex;
extern crate glob;

mod network;

use std::process::Command;
use glob::glob;
use network::Network;
use std::io::prelude::*;
use std::fs::File;

fn main() {
    let config = glob("/etc/wpa_supplicant/wpa_supplicant-*.conf");
    for file in config.unwrap() {
        let mut f = File::open(file.unwrap()).unwrap();
        let mut s = String::new();
        f.read_to_string(&mut s).unwrap();
        print!("{}", s)
    }
    let command = Command::new("iwlist")
                     .arg("wlp2s0")
                     .arg("scan")
                     .output()
                     .unwrap_or_else(|e| { panic!("failed to execute process: {}", e) });
    let out = String::from_utf8_lossy(&command.stdout)
                        .into_owned();
    let split = out.split("Cell");
    let mut output: Vec<&str> = split.collect();
    let mut networks: Vec<Network> = Vec::new();
    output.remove(0);
    for cell in output {
        let network = Network::from_scan(&cell);
        if !networks.contains(&network) && network.name != "" {
            networks.push(network);
        }
    }
    for network in networks {
        println!("{} {} {}", network.name, network.signal, network.encrypted);
    }
}
