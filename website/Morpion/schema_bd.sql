-- Drop schema if exists
DROP SCHEMA IF EXISTS jeu_de_morpion CASCADE;

-- Create schema
CREATE SCHEMA IF NOT EXISTS series;
SET search_path TO series;

-- Table morpion
CREATE TABLE morpion (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255) NOT NULL,
    hp INT NOT NULL,
    attack INT NOT NULL,
    mana INT NOT NULL,
    skill INT NOT NULL
);

-- Table equipe
CREATE TABLE equipe (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,
    creation_date DATE NOT NULL
);

-- Table equipe_morpion
CREATE TABLE equipe_morpion (
    equipe_id INT NOT NULL,
    morpion_id INT NOT NULL,
    PRIMARY KEY(equipe_id, morpion_id),
    FOREIGN KEY(equipe_id) REFERENCES equipe(id),
    FOREIGN KEY(morpion_id) REFERENCES morpion(id)
);

-- Table configuration
CREATE TABLE configuration (
    id SERIAL PRIMARY KEY,
    grid_size INT NOT NULL, -- 3 or 4
    max_turns INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table partie
CREATE TABLE partie (
    id SERIAL PRIMARY KEY,
    equipe1_id INT NOT NULL,
    equipe2_id INT NOT NULL,
    config_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    winning_equipe_id INT NULL,
    max_turns_reached BOOLEAN DEFAULT FALSE,
    FOREIGN KEY(equipe1_id) REFERENCES equipe(id),
    FOREIGN KEY(equipe2_id) REFERENCES equipe(id),
    FOREIGN KEY(config_id) REFERENCES configuration(id)
);

-- Table journal
CREATE TABLE journal (
    partie_id INT NOT NULL,
    seq INT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text TEXT,
    PRIMARY KEY(partie_id, seq),
    FOREIGN KEY(partie_id) REFERENCES partie(id)
);

