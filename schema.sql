CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE folders (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('user', 'system')),
    provider_id VARCHAR(255),
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_folders_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add indexes
CREATE INDEX idx_folders_user_id_name ON folders(user_id, name);
CREATE UNIQUE INDEX unique_folders_provider_user ON folders(provider_id, user_id);

CREATE TABLE emails (
    id BIGSERIAL PRIMARY KEY,
    subject VARCHAR(255),
    provider_id VARCHAR(255) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
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
    id BIGSERIAL PRIMARY KEY,
    email_id BIGINT NOT NULL,
    name VARCHAR(255),
    email_address VARCHAR(255),
    type VARCHAR(10) NOT NULL CHECK (type IN ('to', 'cc')),
    FOREIGN KEY (email_id) REFERENCES emails(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_folders (
    id BIGSERIAL PRIMARY KEY,
    email_id BIGINT NOT NULL,
    folder_id BIGINT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES emails(id),
    FOREIGN KEY (folder_id) REFERENCES folders(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_attachments (
    id BIGSERIAL PRIMARY KEY,
    email_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(255),
    FOREIGN KEY (email_id) REFERENCES emails(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow (
    id BIGSERIAL PRIMARY KEY,
    hash VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_hash ON workflow(hash);

CREATE TABLE workflow_run (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('yet_to_start', 'running', 'completed', 'failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflow(id)
);

CREATE TABLE workflow_run_activity (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,
    email_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('move', 'mark_as_read')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES workflow_run(id),
    FOREIGN KEY (email_id) REFERENCES emails(id)
);


CREATE INDEX idx_emails_sender_name_email ON emails ("sender_name" text_pattern_ops, "sender_email_address" text_pattern_ops);
CREATE INDEX idx_emails_recipient_name_email ON email_recipients ("name" text_pattern_ops, "email_address" text_pattern_ops);
CREATE INDEX idx_emails_subject_tsvector ON emails USING GIN (to_tsvector('english', "subject"));
CREATE INDEX idx_emails_body_plain_text_tsvector ON emails USING GIN (to_tsvector('english', "body_plain_text"));
CREATE INDEX idx_emails_received_timestamp_brin ON emails USING BRIN (received_timestamp);
