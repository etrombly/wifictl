use regex::Regex;

pub struct Network<'a> {
    pub name: &'a str,
    pub signal: &'a str,
    pub encrypted: bool,
}

impl<'a> Network<'a> {
    pub fn new(name: &'a str, signal: &'a str, encrypted: bool) -> Network<'a> {
        Network {
            name: name,
            signal: signal,
            encrypted: encrypted
        }
    }

    pub fn from_scan(scan: &str) -> Network {
        let re = Regex::new(r#"(?ms)Quality=(?P<quality>.*?)\sSignal level=(?P<signal>.*?)\n.*?Encryption key:(?P<key>.*?)\n.*?ESSID:"(?P<essid>.*?)".*?"#).unwrap();
        let caps = re.captures(&scan).unwrap();
        let mut key = false;
        if caps.name("key").unwrap() == "on" {
            key = true;
        }
        Network::new(caps.name("essid").unwrap(),
                     caps.name("signal").unwrap(),
                     key)
    }
}

impl<'a> PartialEq for Network<'a> {
    fn eq(&self, other: &Network) -> bool {
        if self.name == other.name {
            return true
        }
        false
    }
}
