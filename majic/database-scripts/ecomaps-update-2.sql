-- Adding a deleted column to the datasets table
USE ecomaps;

ALTER TABLE datasets ADD COLUMN deleted TINYINT DEFAULT 0;


