CREATE TABLE market_origins (
	id SERIAL PRIMARY KEY,
	marketid INTEGER,
	marketname VARCHAR(150) NOT NULL,
	FOREIGN KEY (marketid) REFERENCES market (marketid)
)

CREATE TABLE market_destination (
	id SERIAL PRIMARY KEY,
	marketid INTEGER,
	marketname VARCHAR(150) NOT NULL,
	FOREIGN KEY (marketid) REFERENCES market (marketid)
)

INSERT INTO market_origins (marketid, marketname)
VALUES (42, 'Jalisco')

INSERT INTO market_destination (marketid, marketname)
VALUES 
(1, 'Sinaloa'),
(10, 'DF: Central de Abasto de Iztapalapa DF'),
(17, 'Hidalgo: Central de Abasto de Pachuca'),
(19, 'Jalisco: Mercado Felipe Ángeles de Guadalajara'),
(23, 'Morelos: Central de Abasto de Cuautla'),
(33, 'Sonora: Mercado de Abasto "Francisco I. Madero" de Hermosillo')