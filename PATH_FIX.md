# Path Fix - Restructure Follow-up

## 🐛 Issue

After reorganizing the project structure, the app couldn't find the default data file when running from the project root.

**Error:**
```
❌ Error loading default file: Data file not found: ../data/raw/contacts_campus_Qro_.csv
```

## 🔍 Root Cause

When running `streamlit run app/streamlit_app.py` from the project root, the current working directory is the project root (`/Users/.../SettingUp`), not the `app/` directory.

The original path `../data/raw/contacts_campus_Qro_.csv` tried to go UP one level from the project root, which was incorrect.

## ✅ Solution

Changed paths to be relative to the project root (where streamlit runs from):

### 1. Data Path Fixed

**File:** `app/utils.py`

**Before:**
```python
file_path = Path("../data/raw/contacts_campus_Qro_.csv")  # ❌ Wrong
```

**After:**
```python
file_path = Path("data/raw/contacts_campus_Qro_.csv")  # ✅ Correct
```

### 2. Logo Path Fixed

**File:** `app/streamlit_app.py`

**Before:**
```python
logo_path = Path("assets/corchetes-blanco.webp")  # ❌ Would fail
```

**After:**
```python
logo_path = Path("app/assets/corchetes-blanco.webp")  # ✅ Correct
```

## 📊 Path Resolution

When running from project root:

```
Current Working Directory: /Users/diegosalinas/Documents/SettingUp/

✅ data/raw/contacts_campus_Qro_.csv
   → /Users/diegosalinas/Documents/SettingUp/data/raw/contacts_campus_Qro_.csv

✅ app/assets/corchetes-blanco.webp
   → /Users/diegosalinas/Documents/SettingUp/app/assets/corchetes-blanco.webp
```

## 🧪 Verification

```bash
cd /Users/diegosalinas/Documents/SettingUp

# Test data loading
python3 -c "import sys; sys.path.insert(0, 'app'); from utils import load_data; \
data = load_data(); print(f'✅ Loaded {len(data):,} rows')"

# Output: ✅ Loaded 128,923 rows
```

## 🎯 Key Principle

**All relative paths should be relative to the project root** because:
- Streamlit is run from project root: `streamlit run app/streamlit_app.py`
- Python's working directory = where you run the command from
- Not where the .py file is located

## 📝 Files Modified

1. `app/utils.py` - Data file path
2. `app/streamlit_app.py` - Logo asset path

## ✅ Status

**Fixed and Verified:**
- ✅ Data loads successfully (128,923 rows)
- ✅ Logo path correct
- ✅ All imports working
- ✅ App ready to run

## 🚀 Running the App

```bash
# From project root
cd /Users/diegosalinas/Documents/SettingUp

# Start the app
streamlit run app/streamlit_app.py

# Or use the script
./scripts/START_STREAMLIT_APP.sh
```

## 💡 Lesson Learned

When organizing code into subdirectories:
1. Decide on a "run location" (usually project root)
2. Make all relative paths relative to that location
3. Test from that location
4. Document the expected run location in README

---

**Fix Applied:** October 20, 2025  
**Status:** ✅ Resolved  
**Impact:** App now works correctly with new structure

