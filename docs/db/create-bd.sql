-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema pet_care_connect
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `pet_care_connect` ;

-- -----------------------------------------------------
-- Schema pet_care_connect
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `pet_care_connect` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci ;
USE `pet_care_connect` ;

-- -----------------------------------------------------
-- Table `pet_care_connect`.`roles`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`roles` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`roles` (
  `id_rol` INT NOT NULL AUTO_INCREMENT,
  `nombre_rol` VARCHAR(50) NOT NULL,
  `descripcion` VARCHAR(150) NULL DEFAULT NULL,
  PRIMARY KEY (`id_rol`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE UNIQUE INDEX `nombre_rol` ON `pet_care_connect`.`roles` (`nombre_rol` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`usuarios`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`usuarios` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `id_rol` INT NOT NULL,
  `nombre` VARCHAR(100) NOT NULL,
  `apellido` VARCHAR(100) NOT NULL,
  `correo` VARCHAR(120) NOT NULL,
  `contrasena_hash` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(20) NULL DEFAULT NULL,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` ENUM('activo', 'inactivo') NOT NULL DEFAULT 'activo',
  PRIMARY KEY (`id_usuario`),
  CONSTRAINT `fk_usuario_rol`
    FOREIGN KEY (`id_rol`)
    REFERENCES `pet_care_connect`.`roles` (`id_rol`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE UNIQUE INDEX `correo` ON `pet_care_connect`.`usuarios` (`correo` ASC) VISIBLE;

CREATE INDEX `fk_usuario_rol` ON `pet_care_connect`.`usuarios` (`id_rol` ASC) VISIBLE;

CREATE INDEX `idx_usuarios_correo` ON `pet_care_connect`.`usuarios` (`correo` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`mascotas`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`mascotas` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`mascotas` (
  `id_mascota` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `nombre` VARCHAR(100) NOT NULL,
  `especie` VARCHAR(50) NOT NULL,
  `raza` VARCHAR(80) NULL DEFAULT NULL,
  `sexo` ENUM('macho', 'hembra') NOT NULL,
  `fecha_nacimiento` DATE NULL DEFAULT NULL,
  `color` VARCHAR(50) NULL DEFAULT NULL,
  `peso` DECIMAL(5,2) NULL DEFAULT NULL,
  `esterilizado` TINYINT(1) NOT NULL DEFAULT '0',
  `alergias` TEXT NULL DEFAULT NULL,
  `observaciones` TEXT NULL DEFAULT NULL,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mascota`),
  CONSTRAINT `fk_mascota_usuario`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `pet_care_connect`.`usuarios` (`id_usuario`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `idx_mascotas_usuario` ON `pet_care_connect`.`mascotas` (`id_usuario` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`alimentacion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`alimentacion` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`alimentacion` (
  `id_alimentacion` INT NOT NULL AUTO_INCREMENT,
  `id_mascota` INT NOT NULL,
  `tipo_alimento` VARCHAR(100) NULL DEFAULT NULL,
  `marca` VARCHAR(100) NULL DEFAULT NULL,
  `cantidad` VARCHAR(50) NULL DEFAULT NULL,
  `frecuencia` VARCHAR(50) NULL DEFAULT NULL,
  `horario` VARCHAR(100) NULL DEFAULT NULL,
  `observaciones` TEXT NULL DEFAULT NULL,
  `fecha_registro` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_alimentacion`),
  CONSTRAINT `fk_alimentacion_mascota`
    FOREIGN KEY (`id_mascota`)
    REFERENCES `pet_care_connect`.`mascotas` (`id_mascota`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `fk_alimentacion_mascota` ON `pet_care_connect`.`alimentacion` (`id_mascota` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`atenciones_medicas`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`atenciones_medicas` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`atenciones_medicas` (
  `id_atencion` INT NOT NULL AUTO_INCREMENT,
  `id_mascota` INT NOT NULL,
  `fecha_atencion` DATE NOT NULL,
  `tipo_atencion` VARCHAR(100) NOT NULL,
  `diagnostico` TEXT NULL DEFAULT NULL,
  `tratamiento_indicado` TEXT NULL DEFAULT NULL,
  `veterinario` VARCHAR(100) NULL DEFAULT NULL,
  `clinica` VARCHAR(120) NULL DEFAULT NULL,
  `observaciones` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id_atencion`),
  CONSTRAINT `fk_atencion_mascota`
    FOREIGN KEY (`id_mascota`)
    REFERENCES `pet_care_connect`.`mascotas` (`id_mascota`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `idx_atenciones_mascota` ON `pet_care_connect`.`atenciones_medicas` (`id_mascota` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`citas_veterinarias`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`citas_veterinarias` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`citas_veterinarias` (
  `id_cita` INT NOT NULL AUTO_INCREMENT,
  `id_mascota` INT NOT NULL,
  `fecha_cita` DATETIME NOT NULL,
  `motivo` VARCHAR(150) NOT NULL,
  `veterinario` VARCHAR(100) NULL DEFAULT NULL,
  `clinica` VARCHAR(120) NULL DEFAULT NULL,
  `estado` ENUM('pendiente', 'realizada', 'cancelada') NOT NULL DEFAULT 'pendiente',
  `observaciones` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id_cita`),
  CONSTRAINT `fk_cita_mascota`
    FOREIGN KEY (`id_mascota`)
    REFERENCES `pet_care_connect`.`mascotas` (`id_mascota`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `idx_citas_mascota` ON `pet_care_connect`.`citas_veterinarias` (`id_mascota` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`recordatorios`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`recordatorios` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`recordatorios` (
  `id_recordatorio` INT NOT NULL AUTO_INCREMENT,
  `id_mascota` INT NOT NULL,
  `tipo_recordatorio` ENUM('vacuna', 'tratamiento', 'cita', 'control', 'otro') NOT NULL,
  `titulo` VARCHAR(120) NOT NULL,
  `descripcion` TEXT NULL DEFAULT NULL,
  `fecha_recordatorio` DATETIME NOT NULL,
  `estado` ENUM('pendiente', 'enviado', 'completado') NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (`id_recordatorio`),
  CONSTRAINT `fk_recordatorio_mascota`
    FOREIGN KEY (`id_mascota`)
    REFERENCES `pet_care_connect`.`mascotas` (`id_mascota`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `idx_recordatorios_mascota` ON `pet_care_connect`.`recordatorios` (`id_mascota` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`tratamientos`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`tratamientos` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`tratamientos` (
  `id_tratamiento` INT NOT NULL AUTO_INCREMENT,
  `nombre_tratamiento` VARCHAR(120) NOT NULL,
  `descripcion` TEXT NULL DEFAULT NULL,
  `medicamento` VARCHAR(120) NULL DEFAULT NULL,
  `dosis` VARCHAR(50) NULL DEFAULT NULL,
  `frecuencia` VARCHAR(50) NULL DEFAULT NULL,
  `fecha_inicio` DATE NOT NULL,
  `fecha_fin` DATE NULL DEFAULT NULL,
  `estado` ENUM('activo', 'finalizado', 'suspendido') NOT NULL DEFAULT 'activo',
  `id_atencion` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id_tratamiento`),
  CONSTRAINT `fk_tratamiento_atencion`
    FOREIGN KEY (`id_atencion`)
    REFERENCES `pet_care_connect`.`atenciones_medicas` (`id_atencion`)
    ON DELETE SET NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `fk_tratamiento_atencion` ON `pet_care_connect`.`tratamientos` (`id_atencion` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `pet_care_connect`.`vacunas`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pet_care_connect`.`vacunas` ;

CREATE TABLE IF NOT EXISTS `pet_care_connect`.`vacunas` (
  `id_vacuna` INT NOT NULL AUTO_INCREMENT,
  `id_mascota` INT NOT NULL,
  `nombre_vacuna` VARCHAR(100) NOT NULL,
  `fecha_aplicacion` DATE NOT NULL,
  `fecha_proxima` DATE NULL DEFAULT NULL,
  `dosis` VARCHAR(50) NULL DEFAULT NULL,
  `veterinario` VARCHAR(100) NULL DEFAULT NULL,
  `observaciones` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id_vacuna`),
  CONSTRAINT `fk_vacuna_mascota`
    FOREIGN KEY (`id_mascota`)
    REFERENCES `pet_care_connect`.`mascotas` (`id_mascota`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE INDEX `idx_vacunas_mascota` ON `pet_care_connect`.`vacunas` (`id_mascota` ASC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
