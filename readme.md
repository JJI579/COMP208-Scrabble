# Scrabble

# How to install

## Backend

```
# Move to backend directory
cd backend
# Create Virtual Environment
python -m venv venv
# Activate Virtual Environment
./venv/Scripts/activate
# Install Requirements
pip install -r requirements
```
### How to Run
```
fastapi dev main.py
```

On first run the Backend database will self initialise the SQLITE3 Database and append all of SOWPODS dictionary words into the database for usage within the website.

## Frontend

```
# Move to frontend directory
cd frontend
# Install node modules use your package manager of choice
bun i
or
npm i

# Run
bun dev
or
npm run dev
```





