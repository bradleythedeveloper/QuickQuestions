DROP DATABASE IF EXISTS quickquestions;
CREATE DATABASE quickquestions;
USE quickquestions;
CREATE TABLE actions(
  ID INT PRIMARY KEY AUTO_INCREMENT,
  serverId VARCHAR(18) NOT NULL,
  name VARCHAR(255) NOT NULL,
  added TIMESTAMP(1) NOT NULL DEFAULT CURRENT_TIMESTAMP(1)
);
CREATE TABLE triggersresponses(
  ID INT PRIMARY KEY AUTO_INCREMENT,
  actionFK INT NOT NULL,
  value TEXT NOT NULL,
  type ENUM('trigger', 'response') NOT NULL,
  added TIMESTAMP(1) NOT NULL DEFAULT CURRENT_TIMESTAMP(1),
  FOREIGN KEY (actionFK) REFERENCES actions(ID)
);
-- -------------------------------------------------
INSERT INTO actions (serverId, name) VALUES ('897499735970152559', 'Applications');
INSERT INTO triggersresponses (actionFK, value, type) VALUES (1, 'Mods', 'trigger'),
(1, 'mod applications', 'trigger'),
(1, 'apps open?', 'trigger'),
(1, 'when will the alskdja open?', 'trigger'),
(1, 'alkdsjalsd', 'trigger'),
(1, 'They will open soon.', 'response'),
(1, 'Have patience', 'response'),
(1, 'Please stop asking.', 'response');
INSERT INTO actions (serverId, name) VALUES ('897499735970152559', 'new users');
INSERT INTO triggersresponses (actionFK, value, type) VALUES (2, "hey I\'m new", 'trigger'),
(2, "Hey there new user!", 'response');