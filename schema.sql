CREATE SCHEMA IF NOT EXISTS `roadstate` ;
USE `roadstate`;

-- -----------------------------------------------------
-- Table `roadstate`.`clusters`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roadstate`.`clusters` ;

CREATE  TABLE IF NOT EXISTS `roadstate`.`clusters` (
  `id` BIGINT NOT NULL AUTO_INCREMENT ,
  `latitude` DOUBLE NULL ,
  `longitude` DOUBLE NULL ,
  `average` FLOAT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `lat` (`latitude` ASC, `longitude` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `roadstate`.`datas`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roadstate`.`datas` ;

CREATE  TABLE IF NOT EXISTS `roadstate`.`datas` (
  `quality_factor` INT NULL ,
  `timestamp` BIGINT NULL ,
  `ref_clusters` BIGINT NULL )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `roadstate`.`zoom_levels`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roadstate`.`zoom_levels` ;

CREATE  TABLE IF NOT EXISTS `roadstate`.`zoom_levels` (
  `zoom_level` INT NULL ,
  `latitude` DOUBLE NULL ,
  `longitude` DOUBLE NULL ,
  `average` FLOAT NULL ,
  `ref_cluster` BIGINT NULL ,
  `radius_lat` DOUBLE NULL ,
  `radius_long` DOUBLE NULL ,
  INDEX `i_zoom_level` (`zoom_level` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Placeholder table for view `roadstate`.`cluster_classes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `roadstate`.`cluster_classes` (`count(*)` INT, `ref_clusters` INT);

DELIMITER //


DROP procedure IF EXISTS `roadstate`.`gen_avg` //
 CREATE PROCEDURE `roadstate`.`gen_avg` (idc BIGINT)
 BEGIN
 DECLARE av FLOAT;
 SELECT AVG(quality_factor) AS average INTO av FROM roadstate.datas WHERE ref_clusters=idc;
 UPDATE roadstate.clusters SET average=av WHERE id=idc;
 END//

DELIMITER //

-- -----------------------------------------------------
-- View `roadstate`.`cluster_classes`
-- -----------------------------------------------------
DROP VIEW IF EXISTS `roadstate`.`cluster_classes` ;
DROP TABLE IF EXISTS `roadstate`.`cluster_classes`;
CREATE  OR REPLACE VIEW `roadstate`.`cluster_classes` AS  select count(*), ref_clusters from roadstate.datas group by ref_clusters;
;
USE `roadstate`;

DELIMITER //

DROP TRIGGER IF EXISTS `roadstate`.`t_calc_avg` //
CREATE TRIGGER roadstate.t_calc_avg AFTER INSERT ON roadstate.datas
FOR EACH ROW 
BEGIN
CALL roadstate.gen_avg(NEW.ref_clusters);
END;
//


DELIMITER //