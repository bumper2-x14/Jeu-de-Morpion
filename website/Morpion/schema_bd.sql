DROP SCHEMA IF EXISTS jeu_de_morpion CASCADE;
CREATE SCHEMA IF NOT EXISTS series;
SET search_path TO series;

CREATE TABLE morpion_template (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  image VARCHAR(255) NOT NULL,
  hp INT NOT NULL,
  attack INT NOT NULL,
  mana INT NOT NULL,
  skill INT NOT NULL
);

CREATE TABLE equipe (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  color VARCHAR(7) NOT NULL,
  creation_date DATE NOT NULL
);

CREATE TABLE equipe_morpion (
  equipe_id INT,
  morpion_id INT,
  PRIMARY KEY(equipe_id, morpion_id),
  FOREIGN KEY(equipe_id) REFERENCES equipe(id),
  FOREIGN KEY(morpion_id) REFERENCES morpion_template(id)
);

CREATE TABLE configuration (
  id INT AUTO_INCREMENT PRIMARY KEY,
  grid_size INT NOT NULL, -- 3 or 4
  max_turns INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE partie (
  id INT AUTO_INCREMENT PRIMARY KEY,
  equipe1_id INT NOT NULL,
  equipe2_id INT NOT NULL,
  config_id INT NOT NULL,
  start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  end_time DATETIME NULL,
  winning_equipe_id INT NULL,
  max_turns_reached BOOLEAN DEFAULT FALSE,
  FOREIGN KEY(equipe1_id) REFERENCES equipe(id),
  FOREIGN KEY(equipe2_id) REFERENCES equipe(id),
  FOREIGN KEY(config_id) REFERENCES configuration(id)
);

CREATE TABLE board_cell (
  partie_id INT,
  row INT,
  col INT,
  morpion_instance_id INT NULL,
  unusable BOOLEAN DEFAULT FALSE,
  PRIMARY KEY(partie_id, row, col),
  FOREIGN KEY(partie_id) REFERENCES partie(id)
);

CREATE TABLE morpion_instance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  template_id INT NOT NULL,
  equipe_id INT NOT NULL,
  hp INT NOT NULL,
  attack INT NOT NULL,
  mana INT NOT NULL,
  skill INT NOT NULL,
  alive BOOLEAN DEFAULT TRUE,
  FOREIGN KEY(template_id) REFERENCES morpion_template(id),
  FOREIGN KEY(equipe_id) REFERENCES equipe(id)
);

CREATE TABLE journal (
  partie_id INT,
  seq INT,
  time DATETIME DEFAULT CURRENT_TIMESTAMP,
  text TEXT,
  PRIMARY KEY(partie_id, seq),
  FOREIGN KEY(partie_id) REFERENCES partie(id)
);

