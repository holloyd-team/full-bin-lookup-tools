# BIN Lookup Website

A full-featured BIN (Bank Identification Number) lookup application with:

- A **SQLite** database containing all BIN records.
- A **web frontend** for users to search BIN information.
- A **RESTful API** for programmatic access to BIN data.
- **Telegram Bot** integration: drop in your bot token to make it live.
- **Admin Panel** for managing BIN entries with authentication.

All BIN entries in the database include the following fields:

1. **BIN** (First 6 Digits)  
2. **Category** (Debit / Credit / Prepaid)  
   - If **Category** is **Prepaid**, the following additional fields apply:  
     - **Reloadable** (Yes / No)  
     - **Can be used Internationally** (Yes / No)  
     - **Maximum Gift Card Balance** (USD amount)  
3. **Company** (e.g., Chase, Wells Fargo, or program type for prepaid, such as “Vanilla Gift Card”)  
4. **Country** (ISO‐formatted, e.g., `USA`)  
5. **Customer Service** (phone number in `1-123-123-1234` format)  
6. **Distributor**  
   - If **Category** is **Prepaid**, this is the program manager (e.g., `InComm Financial Services`).  
   - Otherwise, it is the same as the **Company**.  
7. **Issuer** (Issuing bank name)  
8. **Type** (Debit / Credit; all prepaid cards count as Debit)  
9. **Website URL** (For prepaid: e.g., `vanillagift.com`; for banks: e.g., `chase.com`)

---

## Features

- Searchable web interface to lookup BIN details by entering the first six digits.
- RESTful API endpoints for querying BIN data.
- Telegram Bot integration for real-time lookup via chat.
- Admin Panel (`/admin`) for creating, updating, and deleting BIN entries.
- Mobile, tablet, and desktop responsive design with a simple, elegant UI.

---

## Requirements

- Python 3.8+  
- SQLite 3  
- Flask (or another Python web framework of your choice)  
- SQLAlchemy (or another ORM/library for SQLite)  
- Requests (for API calls, if needed)  
- python-telegram-bot (for Telegram Bot integration)

---

## Installation

1. Clone the repository to your local machine.  
2. Navigate to the project directory.  
3. (Optional) Create and activate a virtual environment:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\\venv\\Scripts\\activate   # Windows ```  
4. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
5. Create the SQLite database file (e.g., `bins.db`) in the project root.

---

## Configuration

For application settings, create a `config.json` file in the project root with the following structure:

```json
{
  "telegram": {
    "enabled": true,        
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN"
  },
  "api": {
    "enabled": true,
    "api_key": "YOUR_API_KEY_OR_EMPTY_STRING"
  },
  "admin": {
    "enabled": true,
    "username": "admin",
    "password": "password123"
  },
  "frontend": {
    "primary_color": "#007BFF",
    "secondary_color": "#0056b3",
    "site_name": "BIN Lookup",
    "logo": {
      "enabled": false,
      "image_url": "",
      "link_url": ""
    },
    "description": "",
    "disclaimer_enabled": true
  },
  "custom_domain": ""
}
```

- **telegram.enabled**: `true` or `false` to run the Telegram bot.  
- **telegram.bot_token**: Your Telegram bot token (required if enabled).  
- **api.enabled**: `true` or `false` to enable the RESTful API.  
- **api.api_key**: API key for authentication. If empty string, no authentication is required.  
- **admin.enabled**: `true` or `false` to enable the Admin Panel.
- **admin.username**: Default username for admin login.
- **admin.password**: Default password for admin login.
- **frontend.primary_color**: Hex color used for the header background.
- **frontend.secondary_color**: Hex color used for buttons and highlights.
- **frontend.site_name**: Text displayed as the site title.
- **frontend.logo.enabled**: Display the logo if `true`.
- **frontend.logo.image_url**: URL of the logo image.
- **frontend.logo.link_url**: URL the logo links to when clicked.
- If a logo URL is provided, it will also be used to generate `favicon.ico` in
  the `static` folder on startup. The Pillow package is required for this
  feature.
- **frontend.description**: Optional text shown below search results.
- **frontend.disclaimer_enabled**: Show the accuracy disclaimer if `true`.
- **custom_domain**: Optional base URL to use on the API documentation page if
  Flask cannot determine the correct domain.

---

## Database Schema

Use a single table named `bins` with the following columns. Only the `bin` column is required (`NOT NULL`); all other fields can be `NULL` if the information isn’t available:

- `id` (INTEGER, Primary Key, Auto-increment)
- `bin` (TEXT, unique, first six digits, `NOT NULL`)
- `category` (TEXT, one of `Debit`, `Credit`, `Prepaid`)
- `reloadable` (TEXT, `Yes` or `No`, `NULL` if not Prepaid)
- `international` (TEXT, `Yes` or `No`, `NULL` if not Prepaid)
- `max_balance` (INTEGER, `NULL` if not Prepaid)
- `company` (TEXT)
- `country` (TEXT, e.g., `USA`)
- `customer_service` (TEXT, e.g., `1-123-123-1234`)
- `distributor` (TEXT)
- `issuer` (TEXT)
- `type` (TEXT, `Debit` or `Credit`)
- `website_url` (TEXT)

Example SQL schema:

```sql
CREATE TABLE IF NOT EXISTS bins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin TEXT NOT NULL UNIQUE,
    category TEXT,
    reloadable TEXT,
    international TEXT,
    max_balance INTEGER,
    company TEXT,
    country TEXT,
    customer_service TEXT,
    distributor TEXT,
    issuer TEXT,
    type TEXT,
    website_url TEXT
);
```

---

## Seeding the Database

1. Prepare a CSV or script containing all BIN records with their fields.
2. Use a seed script (e.g., `seed_bins.py`) that reads the CSV and inserts rows into the `bins` table.
3. Run the seed script:

   ```bash
   python seed_bins.py
   ```
4. Confirm data by opening a SQLite shell:

   ```bash
   sqlite3 bins.db
   sqlite> SELECT COUNT(*) FROM bins;
   ```

---

## Running the Application

1. Ensure the virtual environment is activated (if using one).
2. Populate `config.json` with the necessary Telegram, API, and Admin settings.
3. Start the Flask (or chosen framework) server:

   ```bash
   flask run
   ```
4. By default, the web frontend, API, and Admin Panel will be accessible at `http://127.0.0.1:5000/`.

---

## Web Frontend

- Navigate to `http://127.0.0.1:5000/` in your browser.
- Enter the first six digits of a card’s BIN to search.
- The result page displays all fields associated with that BIN.
- Use search filters or suggestions for faster lookups.
- The design is fully responsive for mobile, tablet, and desktop.

---

## RESTful API

- **GET /api/bin/<bin>**

  - Description: Retrieve BIN record by its first six digits.
  - Authentication: Include `x-api-key: YOUR_API_KEY` header if API authentication is enabled.
  - Response (JSON):

    ```json
    {
      "bin": "123456",
      "category": "Prepaid",
      "reloadable": "Yes",
      "international": "No",
      "max_balance": 500,
      "company": "Vanilla Gift Card",
      "country": "USA",
      "customer_service": "1-800-123-4567",
      "distributor": "InComm Financial Services",
      "issuer": "MetaBank",
      "type": "Debit",
      "website_url": "vanillagift.com"
    }
    ```

- **GET /api/bins?country=<country_code>&category=<category>**

  - Description: Filter BINs by country and/or category.
  - Authentication: Include `x-api-key: YOUR_API_KEY` header if enabled.
  - Response: Array of matching BIN objects.

- **POST /api/report/<bin>**

  - Description: Submit corrections for a BIN without authentication.
  - Request Body (JSON): Fields matching the BIN data structure.
  - Response: Created submission object.

- **POST /api/bin**

  - Description: Add a new BIN record.
  - Authentication: Include `x-api-key: YOUR_API_KEY` header if enabled.
  - Request Body (JSON): Must include all required fields.
  - Response: Created BIN object or validation errors.

- **PUT /api/bin/<bin>**

  - Description: Update existing BIN record.
  - Authentication: Include `x-api-key: YOUR_API_KEY` header if enabled.
  - Request Body (JSON): Fields to update.
  - Response: Updated BIN object.

- **DELETE /api/bin/<bin>**

  - Description: Delete a BIN record by its first six digits.
  - Authentication: Include `x-api-key: YOUR_API_KEY` header if enabled.
  - Response: Success message or error.

---

## Telegram Bot Integration

See `config.json` for enabling/disabling the bot and specifying the token.

When enabled, the bot listens for messages in the format:

```
/lookup 123456
```

When a user sends `/lookup <bin>`, the bot queries the local API or database directly and returns a formatted response:

```
BIN: 123456
Category: Prepaid
Reloadable: Yes
International: No
Max Balance: $500
Company: Vanilla Gift Card
Country: USA
Customer Service: 1-800-123-4567
Distributor: InComm Financial Services
Issuer: MetaBank
Type: Debit
Website: vanillagift.com
```

To start the bot:

```bash
python telegram_bot.py
```  

---

## Admin Panel

Access `http://127.0.0.1:5000/admin` to reach the Admin Panel login page. Use credentials from `config.json`:

- **Username**: `admin` (as set in `config.json`)
- **Password**: `password123` (as set in `config.json`)

After signing in, admin users can:

- **Lookup** an existing BIN by first six digits.
- **Create** a new BIN entry, filling in all available fields.
- **Edit** any existing BIN entry: update Category, Company, Country, etc.
- **Delete** BIN entries if needed.

The Admin Panel is fully responsive and shares the same elegant design language as the public frontend.

---

## Environment Variables

* `FLASK_ENV`: Set to `development` or `production`.
* `DATABASE_URL`: SQLite database path (e.g., `sqlite:///bins.db`).

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write clear commit messages and include tests where applicable.
4. Submit a pull request detailing your changes.
