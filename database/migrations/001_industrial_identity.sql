CREATE SCHEMA IF NOT EXISTS industrial;

CREATE TABLE IF NOT EXISTS industrial.process (
    process_id UUID PRIMARY KEY,
    logical_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS industrial.asset (
    asset_id UUID PRIMARY KEY,
    logical_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,

    process_id UUID NOT NULL
        REFERENCES industrial.process(process_id),

    parent_asset_id UUID
        REFERENCES industrial.asset(asset_id),

    asset_type TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS industrial.variable (
    variable_id UUID PRIMARY KEY,
    logical_name TEXT NOT NULL UNIQUE,

    catalog_item_logical_name TEXT NOT NULL,

    asset_id UUID NOT NULL
        REFERENCES industrial.asset(asset_id),

    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS industrial.source (
    source_id UUID PRIMARY KEY,
    logical_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS industrial.variable_source (
    variable_id UUID NOT NULL
        REFERENCES industrial.variable(variable_id),

    source_id UUID NOT NULL
        REFERENCES industrial.source(source_id),

    PRIMARY KEY (
        variable_id,
        source_id
    )
);

CREATE INDEX IF NOT EXISTS
    ix_variable_source_source_id
ON industrial.variable_source(source_id);
