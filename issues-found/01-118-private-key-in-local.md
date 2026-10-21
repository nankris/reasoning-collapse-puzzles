# 01: an RSA private key is present at .local/colab_rsa (SECURITY)
- `.local/` is gitignored, but the folder is in the Drive snapshot along with vendored paramiko, bcrypt and cffi (aarch64 .so).
- Action before any push or share: make sure `.local/` stays excluded, and consider rotating the key if it was ever authorized anywhere persistent. Not deleted by Grok Bot (rule: don't delete user data).

## Status (21 Oct 2026, 22:40 IST): fixed for GitHub
`.local/` (including `colab_rsa`) is not in this repo. The copy step excludes it, `.gitignore` blocks `**/.local/` and `**/colab_rsa*`, and gitleaks plus a PEM-header regex ran clean before the push. The key is still in the Drive zip `repos/118-reasoning-collapse-puzzles.zip`. If it was ever authorized on a persistent host, rotate it.
