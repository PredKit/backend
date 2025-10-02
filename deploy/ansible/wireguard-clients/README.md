# WireGuard Client Configurations

This directory will contain WireGuard VPN client configurations after running the Ansible playbook.

## ⚠️ Security Warning

Client configuration files contain **private keys** and should be treated as secrets:

- ✅ Keep them secure
- ✅ Never commit to version control (already in .gitignore)
- ✅ Share over secure channels only (encrypted email, password managers, etc.)
- ✅ Delete if compromised and regenerate

## Files Generated

After running `./run.sh`, you'll find:

- `local-dev.conf` - For your local development machine
- `admin-laptop.conf` - For administrative access
- `ci-cd.conf` - For CI/CD pipelines

## Usage

See the parent directory's [WIREGUARD_SETUP.md](../WIREGUARD_SETUP.md) for:
- Installation instructions
- Platform-specific setup (Linux, macOS, Windows, Mobile)
- Connection testing
- Troubleshooting

## Regenerating Configs

If you need to regenerate configs (e.g., if keys are compromised):

1. SSH to server and delete old keys:
   ```bash
   ssh root@<server-ip>
   rm /etc/wireguard/client_*
   ```

2. Re-run Ansible:
   ```bash
   cd deploy/ansible && ./run.sh
   ```

New configs will be downloaded to this directory.

