CREATE TABLE stones (
    id INTEGER PRIMARY KEY,
    stock_number TEXT NOT NULL UNIQUE,

    status TEXT NOT NULL CHECK (status IN ('available', 'hold', 'for memo', 'memo','sold')),

    shape TEXT NOT NULL,
    weight REAL NOT NULL,
    size TEXT NOT NULL,

    color_grade TEXT NOT NULL,
    clarity TEXT NOT NULL,

    measurements TEXT NOT NULL,

    rapaport_price_per_carat REAL,
    rapaport_discount REAL,
    price_per_carat REAL,
    total_price REAL,c

    cut_grade TEXT,
    polish TEXT,
    symmetry TEXT,

    fluorescence_strength TEXT,
    fluorescence_color TEXT,

    fancy_color TEXT,
    fancy_intensity TEXT,
    overtone TEXT,


    depth_percent REAL,
    table_percent REAL,
    girdle TEXT,
    culet TEXT,

    crown_height REAL,
    crown_angle REAL,
    pavilion_depth REAL,
    pavilion_angle REAL,

    eye_clean TEXT,
    bgm TEXT,
    black TEXT,
    milky TEXT,
    open_inclusions TEXT,

    pair_number TEXT,
    pair_stock_number TEXT,
    pair_separable INTEGER,

    picture_link TEXT,
    video_link TEXT
);

CREATE TABLE stone_price_history (
    id INTEGER PRIMARY KEY,
    stone_id INTEGER NOT NULL,
    price_per_carat REAL NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stone_id) REFERENCES stones(id)
);

CREATE TABLE rapaport_prices (
    id INTEGER PRIMARY KEY,

    shape TEXT NOT NULL,
    clarity TEXT NOT NULL,
    color TEXT NOT NULL,

    min_weight REAL NOT NULL,
    max_weight REAL NOT NULL,

    price_per_carat REAL NOT NULL,
    price_date DATE NOT NULL
);

CREATE TABLE certificates (
    id INTEGER PRIMARY KEY,
    stone_id INTEGER NOT NULL,

    report_number TEXT UNIQUE,
    lab TEXT,
    laser_inscription TEXT,

    certificate_comments TEXT,
    key_to_symbols TEXT,
    comments TEXT,

    certificate_image_link TEXT,

    active INTEGER NOT NULL,

    FOREIGN KEY (stone_id) REFERENCES stones(id) ON DELETE CASCADE
);


CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,

    polygon_id INTEGER UNIQUE,
    jbt_id INTEGER UNIQUE,
    rapnet_id INTEGER UNIQUE,

    tax_id TEXT NOT NULL UNIQUE,
    sales_tax_id TEXT NOT NULL UNIQUE
);


CREATE TABLE client_contacts (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    fax TEXT,
    cell TEXT,

    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);


CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,

    client_id INTEGER NOT NULL,

    type TEXT NOT NULL CHECK (type IN ('memo','invoice','credit_invoice')),
    reference_transaction INTEGER,

    status TEXT NOT NULL,

    person TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    fax TEXT,

    date DATE NOT NULL,
    terms TEXT NOT NULL,

    carrier TEXT NOT NULL,
    shipment_type TEXT NOT NULL,
    ship_charge REAL NOT NULL,

    ship_to_address TEXT NOT NULL,

    purchase_order_number TEXT,

    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (reference_transaction) REFERENCES transactions(id)
);


CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY,

    transaction_id INTEGER NOT NULL,
    stone_id INTEGER NOT NULL,

    status TEXT NOT NULL CHECK (status IN ('memo','invoiced','returned')),

    certificate_id INTEGER,

    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (stone_id) REFERENCES stones(id),
    FOREIGN KEY (certificate_id) REFERENCES certificates(id),

    UNIQUE (transaction_id, stone_id)
);