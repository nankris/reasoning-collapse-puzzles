# 01: an RSA private key is present at .local/colab_rsa (SECURITY)
- `.local/` is gitignored, but the folder is in the Drive snapshot along with vendored paramiko, bcrypt and cffi (aarch64 .so).
- Action before any push or share: make sure `.local/` stays excluded, and consider rotating the key if it was ever authorized on a persistent host. I did not delete it from the source snapshot.
