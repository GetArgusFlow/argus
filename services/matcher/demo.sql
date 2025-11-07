-- Creates the demo database schema and populates it with test data.

-- 1. Create the main products table
-- This table holds all product attributes.
CREATE TABLE products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  store_id INT NOT NULL,
  title VARCHAR(255),
  brand VARCHAR(100),
  contents VARCHAR(50),
  unit VARCHAR(50),
  pack VARCHAR(100),
  colors VARCHAR(100),
  type VARCHAR(100),
  ean VARCHAR(255),
  dimensions VARCHAR(100)
);

-- 2. Create the matches table
-- This defines which products are matches (for training).
CREATE TABLE product_matches (
  group_id INT NOT NULL,  -- All products with the same group_id are matches
  product_id INT NOT NULL,
  PRIMARY KEY (group_id, product_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 3. Insert Demo Data

-- Group 1: Coca-Cola (Two matching products)
INSERT INTO products (store_id, title, brand, contents, unit, type) VALUES
(1, 'Coca-Cola Classic', 'Coca-Cola', '1500', 'ml', 'Frisdrank'),
(2, 'Coke Classic 1,5L Fles', 'Coca-Cola', '1500', 'ml', 'Frisdrank');
-- Add to matches
INSERT INTO product_matches (group_id, product_id) VALUES (1, 1), (1, 2);

-- Group 2: Pepsi (A "hard negative" for Coca-Cola)
INSERT INTO products (store_id, title, brand, contents, unit, type) VALUES
(1, 'Pepsi Max', 'Pepsi', '1500', 'ml', 'Frisdrank');
-- Add to matches (it's in its own group of 1)
INSERT INTO product_matches (group_id, product_id) VALUES (2, 3);

-- Group 3: Gallo Wijn (Two matching products)
INSERT INTO products (store_id, title, brand, contents, unit, type, colors) VALUES
(1, 'Gallo Family Chardonnay', 'Gallo', '750', 'ml', 'Wijn', 'wit'),
(2, 'Gallo Chardonnay 750ml', 'Gallo', '750', 'ml', 'Wijn', 'wit');
-- Add to matches
INSERT INTO product_matches (group_id, product_id) VALUES (3, 4), (3, 5);

-- Group 4: Gallo Wijn (A "hard negative" for the Chardonnay)
INSERT INTO products (store_id, title, brand, contents, unit, type, colors) VALUES
(1, 'Gallo Family Merlot', 'Gallo', '750', 'ml', 'Wijn', 'rood');
-- Add to matches
INSERT INTO product_matches (group_id, product_id) VALUES (4, 6);

-- Group 5: Something unrelated
INSERT INTO products (store_id, title, brand, contents, unit, type) VALUES
(2, 'Lays Paprika Chips', 'Lays', '200', 'g', 'Chips');
-- Add to matches
INSERT INTO product_matches (group_id, product_id) VALUES (5, 7);