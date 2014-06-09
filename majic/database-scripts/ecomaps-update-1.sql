-- ECOMAPS 42 and 43
USE ecomaps;
ALTER TABLE datasets ADD COLUMN data_range_from INT DEFAULT 1;
ALTER TABLE datasets ADD COLUMN data_range_to INT DEFAULT 50;
ALTER TABLE datasets ADD COLUMN is_categorical TINYINT DEFAULT 0;


