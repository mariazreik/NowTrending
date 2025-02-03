# ⚠️ WIP - README

This README file is a work in progress, just like other aspects of this repository. 😊

### 📄 Project Plan

To view the project plan, navigate to the `docs` folder and open the file `project_plan.ipynb`.

---

## 🚀 Setting Up the Database and Inserting Data

Follow these steps to set up the database and insert data:

### 1. Create a Virtual Environment and Install Dependencies

Start by creating a virtual environment and installing the necessary dependencies:

```bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment (on macOS/Linux)
source .venv/bin/activate

# On Windows, use:
# .venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt

```
### 2. Create the Database

```bash
python database/database.py
```

### 3. Insert Data into the Database

```bash
python scripts/update_database.py
```

### 4. Keep the Database Updated
To fetch new data and keep the database updated, run the update_database.py script regularly. This script automatically updates the database with the latest data.

```bash
python scripts/update_database.py
```

#### Extra Notes
- The twitter_trends table updates frequently, every 30 minutes or less.
- The twitter_hashtags table updates less frequently, every 24 hours.