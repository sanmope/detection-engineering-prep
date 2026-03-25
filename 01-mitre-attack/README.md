# MITRE ATT&CK Coverage Mapping

## Resources

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [TA453 Threat Report — Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/operation-spoofedscholars-conversation-ta453)
- [TA416 Threat Report — Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/good-bad-and-web-bug-ta416-increases-operational-tempo-against-european)

## What I did

- Created an Enterprise ATT&CK layer in the Navigator
- Mapped techniques detectable with a Kafka/Elasticsearch pipeline
  (background from McAfee SIEM role)
- Analyzed two real Proofpoint threat reports: TA453 (Iran) and TA416 (China)

## Techniques marked as covered

| Technique | ID | Tactic |
|---|---|---|
| Phishing | T1566 | Initial Access |
| Valid Accounts | T1078 | Initial Access |
| Exploit Public-Facing Application | T1190 | Initial Access |
| External Remote Services | T113Initial Access |
| Network Sniffing | T1040 | Credential Access |
| Network Service Discovery | T1046 | Discovery |

## Key insight

Rule-based detection (IOCs) arrives too late for sophisticated actors
like TA453 and TA416. Both groups use legitimate infrastructure
(Google Drive, compromised academic sites) and build rapport before
delivering payloads. Behavioral detection (UEBA) and sequence
correlation are required — exactly what the ML pipeline in
02-ml-anoly-detection implements.

## Coverage layer

Saved as `coverage_layer.json` — load at
https://mitre-attack.github.io/attack-navigator/
