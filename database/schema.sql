PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    category_id INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS transaction_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    purchase_cost INTEGER NOT NULL,
    current_value INTEGER NOT NULL,
    acquired_date DATE NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    purchase_cost INTEGER NOT NULL,
    sale_price INTEGER,
    acquired_date DATE NOT NULL,
    sold_date DATE,
    status TEXT NOT NULL DEFAULT 'AVAILABLE',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS receivables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    original_amount INTEGER NOT NULL,
    date_created DATE NOT NULL,
    due_date DATE,
    status TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES people(id)
);

CREATE TABLE IF NOT EXISTS credit_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    credit_limit INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS liabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    credit_account_id INTEGER,
    description TEXT NOT NULL,
    original_amount INTEGER NOT NULL,
    date_created DATE NOT NULL,
    due_date DATE,
    status TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES people(id),
    FOREIGN KEY (credit_account_id) REFERENCES credit_accounts(id)
);

CREATE TABLE IF NOT EXISTS receivable_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receivable_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (receivable_id) REFERENCES receivables(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

CREATE TABLE IF NOT EXISTS liability_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    liability_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (liability_id) REFERENCES liabilities(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);