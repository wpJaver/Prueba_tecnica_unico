DROP DATABASE IF EXISTS pedidos_db;

CREATE DATABASE pedidos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pedidos_db;

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE ciudades (
    id_ciudad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ciudad VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE meses (
    id_mes INT AUTO_INCREMENT PRIMARY KEY,
    nombre_mes VARCHAR(20) NOT NULL UNIQUE
);


CREATE TABLE anios (
    id_anio INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL UNIQUE
);


CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_producto INT NOT NULL,
    id_ciudad INT NOT NULL,
    id_mes INT NOT NULL,
    id_anio INT NOT NULL,
    cantidad INT NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    audit_date DATETIME DEFAULT NOW(),
    

    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
    FOREIGN KEY (id_mes) REFERENCES meses(id_mes),
    FOREIGN KEY (id_anio) REFERENCES anios(id_anio)
);

SET FOREIGN_KEY_CHECKS = 1;
