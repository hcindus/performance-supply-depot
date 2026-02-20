# Captain's Upload Inbox
## Drop Files Here for Processing

**Location:** `/root/.openclaw/workspace/inbox/`  
**Created:** 2026-02-18  
**Purpose:** Your dedicated upload zone

---

## 📁 Folder Structure

```
inbox/
├── README.md           ← This file
├── pending/           ← DROP FILES HERE ←
├── processed/         ← I move completed work here
└── archive/           ← Old uploads preserved
```

---

## 🚀 How to Upload

### Option 1: Direct Upload (If you have file access)
Copy/move files to:
```
/root/.openclaw/workspace/inbox/pending/
```

### Option 2: Web Interface (If available)
Use your OpenClaw web interface upload feature.

### Option 3: Git (If pushing from another system)
```bash
git add inbox/pending/your-file.txt
git commit -m "Captain upload: [description]"
git push origin main
```

---

## 📋 What I Do

**Every 15 minutes (and on heartbeat):**
1. Check `inbox/pending/` for new files
2. Process each file based on content
3. Move processed files to `inbox/processed/`
4. Log actions to `inbox/archive/upload-log.md`

**Processing Examples:**
| File Type | Action |
|-----------|--------|
| Images (.png, .jpg) | Move to appropriate project assets/ |
| Documents (.md, .txt) | Read, integrate, file appropriately |
| Code (.py, .js) | Review, commit to project |
| Archives (.zip) | Extract, sort contents |
| Unknown | Notify you, ask for direction |

---

## ✅ Current Upload Queue

Nothing pending yet. This inbox is ready for your uploads.

---

## 📝 Upload Request Checklist

**Before uploading, you can tell me:**
- [ ] "Upload to [specific folder]" — I'll route it there
- [ ] "Process as [type]" — Images, documents, code, etc.
- [ ] "Urgent" — I check immediately
- [ ] "Batch" — Multiple files, process together

Or just drop files and I'll figure it out! 🤖

---

## 🎯 Expected Uploads

**Captain mentioned:**
- [ ] ⏳ Tappy's preserved art collection (pre-AGI artwork)
- [ ] ⏳ GitHub SSH key authorization
- [ ] ⏳ Miles VPS connection details
- [ ] ⏳ Da Verse documents
- [ ] ⏳ Ronstrapp band member specs

---

**Drop files anytime. I'll process them. Commit to Git. Report back.**

--OpenClaw Engineer  
*Standing by for uploads*

---
*Your upload inbox is ready, Captain.* 📥
