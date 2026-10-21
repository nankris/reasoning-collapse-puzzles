# 01: an RSA private key is present at .local/colab_rsa (SECURITY)
- `.local/` is gitignored, but the folder is in the Drive snapshot along with vendored paramiko, bcrypt and cffi (aarch64 .so).
- Action before any push or share: make sure `.local/` stays excluded, and consider rotating the key if it was ever authorized anywhere persistent. Not deleted by Grok Bot (rule: don't delete user data).
