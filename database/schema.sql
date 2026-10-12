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
    FOREIGN KEY (transaction_id)
        REFERENCES transactions(id) ON DELETE RESTRICT,
    FOREIGN KEY (account_id)
        REFERENCES accounts(id) ON DELETE RESTRICT
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

CREATE TABLE IF NOT EXISTS asset_valuations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    valuation_date DATE NOT NULL,
    value INTEGER NOT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id)
        REFERENCES assets(id) ON DELETE RESTRICT,
    UNIQUE (asset_id, valuation_date),
    CHECK (value >= 0)
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

CREATE TABLE IF NOT EXISTS receivable_balance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receivable_id INTEGER NOT NULL,
    effective_date DATE NOT NULL,
    outstanding_amount INTEGER NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (receivable_id)
        REFERENCES receivables(id) ON DELETE RESTRICT,
    UNIQUE (receivable_id, effective_date),
    CHECK (outstanding_amount >= 0)
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
    FOREIGN KEY (credit_account_id)
        REFERENCES credit_accounts(id)
);

CREATE TABLE IF NOT EXISTS liability_balance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    liability_id INTEGER NOT NULL,
    effective_date DATE NOT NULL,
    outstanding_amount INTEGER NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (liability_id)
        REFERENCES liabilities(id) ON DELETE RESTRICT,
    UNIQUE (liability_id, effective_date),
    CHECK (outstanding_amount >= 0)
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

CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(date);

CREATE INDEX IF NOT EXISTS idx_transactions_type_date
    ON transactions(type, date);

CREATE INDEX IF NOT EXISTS idx_transaction_entries_account
    ON transaction_entries(account_id);

CREATE INDEX IF NOT EXISTS idx_transaction_entries_transaction
    ON transaction_entries(transaction_id);

CREATE INDEX IF NOT EXISTS idx_asset_valuations_date
    ON asset_valuations(asset_id, valuation_date DESC);

CREATE INDEX IF NOT EXISTS idx_receivable_history_date
    ON receivable_balance_history(
        receivable_id,
        effective_date DESC
    );

CREATE INDEX IF NOT EXISTS idx_liability_history_date
    ON liability_balance_history(
        liability_id,
        effective_date DESC
    );

CREATE INDEX IF NOT EXISTS idx_receivable_payments_date
    ON receivable_payments(date);

CREATE INDEX IF NOT EXISTS idx_liability_payments_date
    ON liability_payments(date);