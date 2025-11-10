DROP SCHEMA IF EXISTS jeu_de_morpion CASCADE;
CREATE SCHEMA IF NOT EXISTS jeu_de_morpion;
SET search_path TO jeu_de_morpion;

CREATE TABLE morpion (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255) NOT NULL,
    hp INT NOT NULL,
    attack INT NOT NULL,
    mana INT NOT NULL,
    skill INT NOT NULL
);

CREATE TABLE equipe (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,
    creation_date DATE NOT NULL
);

CREATE TABLE equipe_morpion (
    equipe_id INT NOT NULL,
    morpion_id INT NOT NULL,
    PRIMARY KEY(equipe_id, morpion_id),
    FOREIGN KEY(equipe_id) REFERENCES equipe(id),
    FOREIGN KEY(morpion_id) REFERENCES morpion(id)
);

CREATE TABLE configuration (
    id SERIAL PRIMARY KEY,
    grid_size INT NOT NULL, -- 3 or 4
    max_turns INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE journal (
    partie_id INT NOT NULL,
    seq INT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text TEXT,
    PRIMARY KEY(partie_id, seq),
    FOREIGN KEY(partie_id) REFERENCES partie(id)
);


INSERT INTO morpion (name, image, hp, attack, mana, skill) VALUES
('Flamix', 'static/img/t1.png', 120, 30, 50, 70),
('Aquarion', 'static/img/t2.png', 140, 25, 80, 65),
('Terranox', 'static/img/t3.png', 200, 20, 40, 50),
('Voltorn', 'static/img/t4.png', 110, 40, 60, 75),
('Frostine', 'static/img/t5.png', 130, 28, 90, 80),
('Shadowen', 'static/img/t6.png', 100, 45, 70, 90),
('Lumina', 'static/img/t7.png', 150, 22, 100, 85),
('Venorax', 'static/img/t8.png', 160, 35, 55, 60),
('Pyrax', 'static/img/t9.png', 125, 38, 45, 72),
('Mystleaf', 'static/img/t10.png', 170, 24, 75, 68);