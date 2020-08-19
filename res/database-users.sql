USE social_network;

CREATE USER IF NOT EXISTS 'webapp'@'localhost' IDENTIFIED BY '11111';
GRANT SELECT, DELETE, INSERT, UPDATE ON social_network.* TO webapp@'localhost';

CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY '22222';
GRANT ALL PRIVILEGES ON social_network.* TO 'admin'@'localhost';
