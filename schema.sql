CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('user', 'system')),
    provider_id VARCHAR(255),
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_folders_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add indexes
CREATE INDEX idx_folders_user_id_name ON folders(user_id, name);
CREATE UNIQUE INDEX unique_folders_provider_user ON folders(provider_id, user_id);

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(255),
    provider_id VARCHAR(255) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    body TEXT,
    body_plain_text TEXT,
    received_timestamp TIMESTAMP,
    sender_name VARCHAR(255),
    sender_email_address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_emails_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE email_recipients (
    id SERIAL PRIMARY KEY,
    email_id INT NOT NULL,
    name VARCHAR(255),
    email_address VARCHAR(255),
    type VARCHAR(10) NOT NULL CHECK (type IN ('to', 'cc')),
    FOREIGN KEY (email_id) REFERENCES emails(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_folders (
    id SERIAL PRIMARY KEY,
    email_id INT NOT NULL,
    folder_id INT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES emails(id),
    FOREIGN KEY (folder_id) REFERENCES folders(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_attachments (
    id SERIAL PRIMARY KEY,
    email_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(255),
    FOREIGN KEY (email_id) REFERENCES emails(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
