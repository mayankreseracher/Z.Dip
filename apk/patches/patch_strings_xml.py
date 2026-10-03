import re

xml_path = "/home/insectoid/apk_build/zytor_decompiled/res/values/strings.xml"
with open(xml_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    'name="settings_title_dweb">Web3 &amp; IPFS Settings<': 'name="settings_title_dweb">Cloud Storage &amp; Remotes (bclone)<',
    'name="settings_desc_dweb">Configure Web3 Services &amp; Gateways<': 'name="settings_desc_dweb">Sync, copy, or stream directly to Terabox, GDrive, Crypt<',
    'name="web3_subtitle">Web3 Settings<': 'name="web3_subtitle">Cloud Storage (bclone)<',
    'name="web3_enable">Enable Web3<': 'name="web3_enable">Enable Cloud Remotes (bclone)<',
    'name="web3_provider">Web3 Provider<': 'name="web3_provider">Active Remote Target<',
    'name="web3_network">Network<': 'name="web3_network">Cloud Remote Provider<',
    'name="web3_network_desc">Select network<': 'name="web3_network_desc">Terabox, Google Drive, Alist, Alldebrid, WebDAV, Crypt<',
    'name="web3_walletconnect">WalletConnect<': 'name="web3_walletconnect">Auto-Sync on Download Complete<',
    'name="filecoin_subtitle">Filecoin Settings<': 'name="filecoin_subtitle">Security &amp; Encryption Vault<',
    'name="filecoin_enable">Enable Filecoin<': 'name="filecoin_enable">Client-Side Encryption (AES-256 Crypt)<',
    'name="filecoin_api_key">API Key<': 'name="filecoin_api_key">Remote Target Path<',
    'name="filecoin_api_key_desc">Configure key<': 'name="filecoin_api_key_desc">Destination cloud folder (e.g. /ZytorDownloads)<',
    'name="filecoin_advanced">Advanced<': 'name="filecoin_advanced">bclone Vault Engine<',
    'name="filecoin_advanced_desc">Configure settings<': 'name="filecoin_advanced_desc">Zero-knowledge encrypted cloud storage bridge<',
    'name="tor_desc">This page will provide tools and resources for accessing TOR networks and decentralized web applications.<': 'name="tor_desc">TOR Onion Routing is active! All media downloads and stream queries route anonymously through the TOR SOCKS5 daemon (127.0.0.1:9050). Configure circuits and bridge settings in Settings &gt; TOR.<',
}

count = 0
for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        count += 1
    else:
        print(f"Warning: pattern not matched: {old}")

with open(xml_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Patched {count} strings in strings.xml successfully!")
