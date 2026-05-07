# Support Cache

This directory contains the small `tiktoken` BPE file used to avoid a runtime network dependency during Arena-Hard answer generation.

File:

```text
o200k_base.tiktoken
```

Original URL:

```text
https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken
```

Expected SHA256:

```text
446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
```

Remote cache key/path used by `tiktoken`:

```text
/zhdd/home/tjshen/260415_ArcherA100/shared_cache/tiktoken/fb374d419588a4632f3f557e76b4b70aebbca790
```

To pre-seed a remote machine:

```bash
mkdir -p /zhdd/home/tjshen/260415_ArcherA100/shared_cache/tiktoken
cp o200k_base.tiktoken /zhdd/home/tjshen/260415_ArcherA100/shared_cache/tiktoken/fb374d419588a4632f3f557e76b4b70aebbca790
sha256sum /zhdd/home/tjshen/260415_ArcherA100/shared_cache/tiktoken/fb374d419588a4632f3f557e76b4b70aebbca790
```
