# PeerLink OCI Security Hardening Implementation Record

## Scope and safety boundaries

- Implementation date: 21 July 2026
- OCI tenancy: `hamza9896`
- Production VM: `p2p-server` in Riyadh (`me-riyadh-1`)
- Backup bucket: `p2p-backups` in Jeddah (`me-jeddah-1`)
- Cost boundary: only controls confirmed as free or within documented OCI free allowances were enabled.
- Production safety: no reboot, package-upgrade run, production DNS change, WAF cutover, public-media access change, or database/application configuration change was performed.

## Implemented and verified

### Network and obsolete workload cleanup

- Removed internet ingress for TCP 5173, 8000, and 8520. The remaining public TCP rules are 22, 80, and 443.
- Confirmed the PeerLink application ports 5173 and 8000 remain bound to loopback only.
- Stopped the obsolete TicketOptix containers and confirmed their restart policy is disabled.
- Confirmed the live PeerLink HTTPS endpoint still returns HTTP 200 after the changes.

### Guest operating-system controls

- Installed and enabled ClamAV signature updates and a daily PeerLink scan timer.
- Completed a test scan with zero infected files.
- Enabled and verified Fail2ban.
- Verified unattended security updates are enabled.
- Hardened SSH with key-only authentication, root-login restrictions, idle-session controls, a warning banner, strong MACs, `AllowTcpForwarding no`, and `MaxSessions 4`.
- Validated the SSH configuration and opened a new SSH connection after the reload.
- Kept the existing 370-day local PeerLink/system log archive enabled.

### OCI Cloud Guard and Vulnerability Scanning

- Enabled Cloud Guard Standard for the tenancy with detector-based monitoring and no automatic remediation responders.
- Created `peerlink-host-security-scan` and target `peerlink-production-hosts` using the free OCI Vulnerability Scanning agent, daily host scans, biweekly file scans, top-1000-port scanning, CIS checks, and `/home/ubuntu/P2P-V2` file scope.
- Verified the target is Active and the first scan completed.
- The first scan reported 1,000 package findings, 11 observed ports, and 14 of 18 CIS checks passing. The four reported SSH CIS failures were corrected afterward; the next scheduled scan must verify the expected 18 of 18 result.

### Notifications, events, monitoring, and cost alerts

- Created Notifications topic `peerlink-security-alerts` for `aadil@iiotsolutions.sa` and `hamza@iiotsolutions.sa`. Aadil's subscription is Active; Hamza's remains Pending recipient confirmation.
- Created active event rules for Cloud Guard problems and material compute state changes, including termination, infrastructure failure, and maintenance events.
- Created active Monitoring alarms for:
  - VM infrastructure unreachability after two minutes;
  - sustained CPU utilization above 90% for ten minutes; and
  - sustained memory utilization above 90% for ten minutes.
- Routed all three alarms to `peerlink-security-alerts` without repeat notifications.
- Created active tenancy-wide cost anomaly monitor `peerlink-all-costs`, with an alert at EUR 1 or 20% and notification group `peerlink-cost-alerts` for Aadil and Hamza.
- Cost anomaly detection requires sufficient historical spend data (normally about 60 days) before it can reliably establish a baseline.

### Centralized security logging

- Created log group `peerlink-security-logs` and custom log `peerlink-host-security`.
- Created dynamic group `PeerLinkLoggingAgents`, limited to the `p2p-server` instance, and the required Logging IAM policies.
- Created active agent configuration `peerlink-security-log-collector` for:
  - `/var/log/auth.log`
  - `/var/log/fail2ban.log`
  - `/var/log/nginx/access.log`
  - `/var/log/nginx/error.log`
- Verified that the VM downloaded the 1,339-byte OCI logging configuration, started tailing all four files, uploaded the buffered events, and that current SSH/authentication events are visible in the OCI `peerlink-host-security` log.

### Backup protection

- Verified the Jeddah `p2p-backups` bucket is private and encrypted with Oracle-managed keys.
- Added active, unlocked 30-day time-bound retention rule `peerlink-backup-30-day-protection`.
- Versioning was deliberately not enabled because each daily backup already uses a unique object name and indefinite deleted-version retention could create avoidable storage growth and charges.

### Bastion

- Created active free standard Bastion `PeerLinkAdminBastion` for `p2p-vcn` / `p2p-public-subnet`.
- Restricted the source allowlist to the administrator's current public address, `151.254.23.244/32`.
- Direct public SSH remains available until a Bastion session is separately tested and the operational cutover is approved.

### Staged WAF and load balancer

- Created the first WAF policy `peerlink-web-protection` under the documented free allowance.
- Added all 29 Oracle-recommended managed protection capabilities with request-body inspection in `Check` (detection-only) mode.
- Created `peerlink-staging-waf-lb`, the first flexible load balancer, fixed at the free 10 Mbps minimum and maximum.
- Attached the WAF policy, enabled active-resource deletion protection, and configured `p2p-server` (`10.0.1.125:80`) as the backend.
- Configured an HTTP listener on port 80 for staging only. The load balancer is Active, its backend set is healthy, and a controlled request returned the expected PeerLink HTTPS redirect with an OCI request ID.
- Enabled load-balancer access and error logs in `peerlink-security-logs` with one-month retention.
- Enabled WAF service log `peerlink-waf-all` in `peerlink-security-logs` with one-month retention.
- Verified the WAF log with a harmless SQL-injection-pattern test request. `PeerLinkManagedProtections` matched rule IDs `9421000_v002` and `9421000_v001`, recorded the request and backend response, and allowed it as expected because the WAF remains in `Check` mode.
- Staging public IP: `145.241.153.36`.
- Production DNS still points directly to the VM. The WAF does not protect production traffic until HTTPS certificate handling, controlled testing, and a separately approved DNS cutover are completed.

## Pending user or maintenance actions

1. Hamza must confirm the OCI Notifications subscription email. Aadil's subscription is already Active.
2. Review the 1,000 Vulnerability Scanning findings, prioritize applicable security updates, and schedule a production maintenance window.
3. Apply the pending package updates and perform the required reboot only during that approved maintenance window.
4. Verify the next Vulnerability Scanning CIS result after the SSH corrections.
5. Test a time-limited Bastion SSH session before considering any restriction of public port 22.
6. Import or issue an appropriate TLS certificate, test HTTPS through the staged load balancer/WAF, and obtain explicit approval before changing production DNS.
7. Monitor Logging, WAF requests, Monitoring datapoints, and Notifications email volume so they remain within their free allowances.

## Deliberately not enabled

- OCI Network Firewall/IDPS: the firewall instance is billable even though part of its processed-data allowance is free.
- Cloud Guard Instance Security Enterprise: billable.
- OCI Health Checks endpoint monitor: billable per monitored endpoint.
- Boot-volume cross-region replication: billable and operationally significant.
- Security Zones, Zero Trust Packet Routing, and public-media bucket access changes: require architecture and application-impact review.
- Object Storage versioning for the unique-name daily backup bucket: unnecessary cost-growth risk.
- Production WAF/DNS cutover, public-SSH removal, package upgrades, and reboot: require separate operational approval.
