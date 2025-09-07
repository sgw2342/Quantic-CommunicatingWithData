-- SCHEMA: production

-- DROP SCHEMA IF EXISTS production;

CREATE SCHEMA IF NOT EXISTS production
    AUTHORIZATION postgres;

-- Table: production.product_categories

-- DROP TABLE IF EXISTS production.product_categories;

CREATE TABLE IF NOT EXISTS production.product_categories
(
    product_category_id integer NOT NULL,
    product_category_type character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT product_categories_pkey PRIMARY KEY (product_category_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.product_categories
    OWNER to postgres;

-- Table: production.product_types

-- DROP TABLE IF EXISTS production.product_types;

CREATE TABLE IF NOT EXISTS production.product_types
(
    product_type_id integer NOT NULL,
    product_type character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT product_types_pkey PRIMARY KEY (product_type_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.product_types
    OWNER to postgres;

-- Table: production.stores

-- DROP TABLE IF EXISTS production.stores;

CREATE TABLE IF NOT EXISTS production.stores
(
    store_id integer NOT NULL,
    store_location character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT store_pkey PRIMARY KEY (store_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.stores
    OWNER to postgres;

-- Table: production.products

-- DROP TABLE IF EXISTS production.products;

CREATE TABLE IF NOT EXISTS production.products
(
    product_id integer NOT NULL,
    base_price double precision NOT NULL,
    product_category_id integer NOT NULL,
    product_type_id integer NOT NULL,
    product_detail character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT products_pkey PRIMARY KEY (product_id),
    CONSTRAINT foreign_key_product_category_id FOREIGN KEY (product_category_id)
        REFERENCES production.product_categories (product_category_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT foreign_key_product_type_id FOREIGN KEY (product_type_id)
        REFERENCES production.product_types (product_type_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.products
    OWNER to postgres;

-- Table: production.transactions

-- DROP TABLE IF EXISTS production.transactions;

CREATE TABLE IF NOT EXISTS production.transactions
(
    transaction_id integer NOT NULL,
    transaction_date date NOT NULL,
    transaction_time time without time zone NOT NULL,
    store_id integer NOT NULL,
    CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id),
    CONSTRAINT foreign_key_store_id FOREIGN KEY (store_id)
        REFERENCES production.stores (store_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.transactions
    OWNER to postgres;

-- Table: production.transaction_details

-- DROP TABLE IF EXISTS production.transaction_details;

CREATE TABLE IF NOT EXISTS production.transaction_details
(
    transaction_detail_id integer NOT NULL,
    transaction_id integer NOT NULL,
    product_id integer NOT NULL,
    transaction_qty integer NOT NULL,
    unit_price double precision,
    CONSTRAINT transaction_details_pkey PRIMARY KEY (transaction_detail_id),
    CONSTRAINT foreign_key_transaction_id FOREIGN KEY (transaction_id)
        REFERENCES production.transactions (transaction_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT foreign_key_product_id FOREIGN KEY (product_id)
        REFERENCES production.products (product_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL

)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS production.transaction_details
    OWNER to postgres;


