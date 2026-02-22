# Ronstrapp Keystore - SAVED FOR LATER USE

## Generated: 2026-02-21

### Keystore Details
- **Path:** `/root/.openclaw/workspace/ronstrapp_release.keystore`
- **Alias:** ronstrapp
- **Algorithm:** RSA 2048-bit
- **Valid Until:** July 9, 2053

### Passwords
- **Store:** mil0nr0s2026
- **Key:** mil0nr0s2026

### Fingerprints

**SHA1:**
```
D7:C4:BA:B8:B5:28:6C:85:C1:8B:22:72:97:64:27:A9:27:F5:E6:95
```

**SHA256:**
```
1D:DC:FC:7C:0A:E4:32:CE:F7:83:DA:70:2E:ED:A8:E8:83:CD:90:F8:54:AC:C0:9A:F0:BA:F9:A4:F5:C4:64:77
```

---

## Usage

```bash
# Export certificate
keytool -exportcert -alias ronstrapp -keystore ronstrapp_release.keystore -file release.cer

# Sign APK
apksigner sign --ks ronstrapp_release.keystore --ks-key-alias ronstrapp --ks-pass pass:mil0nr0s2026 --key-pass pass:mil0nr0s2026 app.apk
```

---

*Saved for later use*
