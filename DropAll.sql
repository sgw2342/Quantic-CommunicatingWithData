

-- drop tables

DROP TABLE IF EXISTS production.product_categories CASCADE;
DROP TABLE IF EXISTS production.stores CASCADE;
DROP TABLE IF EXISTS production.products CASCADE;
DROP TABLE IF EXISTS production.transactions CASCADE;
DROP TABLE IF EXISTS production.transaction_details CASCADE;
DROP TABLE IF EXISTS production.product_types CASCADE;

-- drop the schemas

DROP SCHEMA IF EXISTS production;