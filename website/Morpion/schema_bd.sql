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
    grid_size INT NOT NULL, -- 3 ou 4
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
('Flamix', 't1.png', 4, 4, 3, 4),
('Aquarion', 't2.png', 3, 4, 4, 4),
('Terranox', 't3.png', 5, 3, 3, 4),
('Voltorn', 't4.png', 3, 5, 3, 4),
('Frostine', 't5.png', 4, 3, 4, 4),
('Shadowen', 't6.png', 3, 5, 4, 3),
('Lumina', 't7.png', 4, 3, 5, 3),
('Venorax', 't8.png', 4, 4, 3, 4),
('Pyrax', 't9.png', 3, 4, 4, 4),
('Mystleaf', 't10.png', 4, 3, 4, 4),
('Blazefang', 't11.png', 4, 4, 3, 4),
('Aqualis', 't12.png', 3, 5, 4, 3),
('Terrafin', 't13.png', 3, 4, 4, 4),
('Voltis', 't14.png', 5, 3, 4, 3),
('Frostwing', 't15.png', 4, 3, 4, 4),
('Shadowclaw', 't16.png', 3, 5, 3, 4);

INSERT INTO equipe (name, color, creation_date) VALUES
('Red Dragons', '#FF0000', CURRENT_DATE),
('Blue Phoenix', '#0000FF', CURRENT_DATE),
('Green Titans', '#00FF00', CURRENT_DATE);


INSERT INTO equipe_morpion (equipe_id, morpion_id) VALUES
(1,1), (1,2), (1,3), (1,4), (1,5), (1,6);

INSERT INTO equipe_morpion (equipe_id, morpion_id) VALUES
(2,7), (2,8), (2,9), (2,10), (2,11), (2,12);

INSERT INTO equipe_morpion (equipe_id, morpion_id) VALUES
(3,1), (3,2), (3,3), (3,4), (3,5), (3,6), (3,13), (3,14);
