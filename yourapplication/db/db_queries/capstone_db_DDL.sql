
-- -----------------------------------------------------
-- Schema capstone_db
-- -----------------------------------------------------
DROP DATABASE IF EXISTS capstone_db;
CREATE SCHEMA IF NOT EXISTS `capstone_db` DEFAULT CHARACTER SET utf8 ;
USE `capstone_db` ;



-- -----------------------------------------------------
-- Table `capstone_db`.`Projects`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Projects` (
  `project_id` INT NOT NULL AUTO_INCREMENT,
  `algorithm_id` VARCHAR(145) NOT NULL,
  `project_name` VARCHAR(1025) NOT NULL,
  `project_root_filepath` VARCHAR(1025) NOT NULL,
  `project_config_filename` VARCHAR(1025) NOT NULL,
  `algorithm_file_path` VARCHAR(1025) NOT NULL,
  `algorithm_language` VARCHAR(145) NOT NULL,
  PRIMARY KEY (`project_id`),
  UNIQUE INDEX `project_name_UNIQUE` (`project_name` ASC) VISIBLE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `capstone_db`.`Configurations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Configurations` (
  `configuration_id` INT NOT NULL AUTO_INCREMENT,
  `configuration_parameters` JSON NULL,
  `configuration_file_path` VARCHAR(1025) NOT NULL,
  PRIMARY KEY (`configuration_id`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `capstone_db`.`Backtests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Backtests` (
  `backtest_id` INT NOT NULL AUTO_INCREMENT,
  `project_id` INT NOT NULL,
  `configuration_id` INT NOT NULL,
  `backtest_name` VARCHAR(1025) NOT NULL,
  `backtest_order_events_file_path` VARCHAR(1025),
  `backtest_file_path` VARCHAR(1025) NOT NULL,
  `algorithm_config_filepath` VARCHAR(1025) NOT NULL,
  `rolling_window` JSON NULL,
  `total_performance` JSON NULL DEFAULT NULL,
  `alpha_runtime_statistics` JSON NULL,
  `charts` JSON NULL,
  `orders` JSON NULL,
  `profit_loss` JSON NULL,
  `statistics` JSON NULL,
  `runtime_statistics` JSON NULL,
  `algorithm_configuration` JSON NULL,
  `backtest_orders` JSON NULL,
  PRIMARY KEY (`backtest_id`),
  INDEX `fk_Backtests_Projects_idx` (`project_id` ASC) VISIBLE,
  UNIQUE INDEX `backtest_name_UNIQUE` (`backtest_name` ASC) VISIBLE,

  CONSTRAINT `fk_Backtests_Projects`
    FOREIGN KEY (`project_id`)
    REFERENCES `capstone_db`.`Projects` (`project_id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Backtests_Configurations`
    FOREIGN KEY (`configuration_id`)
    REFERENCES `capstone_db`.`Configurations` (`configuration_id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;




-- -----------------------------------------------------
-- Table `capstone_db`.`Project_Configurations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Project_Configurations` (
  `configuration_id` INT NOT NULL,
  `project_id` INT NOT NULL,
  INDEX `fk_Project_Configurations_Configurations1_idx` (`configuration_id` ASC) VISIBLE,
  INDEX `fk_Project_Configurations_Projects1_idx` (`project_id` ASC) VISIBLE,
  CONSTRAINT `fk_Project_Configurations_Configurations1`
    FOREIGN KEY (`configuration_id`)
    REFERENCES `capstone_db`.`Configurations` (`configuration_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Project_Configurations_Projects1`
    FOREIGN KEY (`project_id`)
    REFERENCES `capstone_db`.`Projects` (`project_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `capstone_db`.`Data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Data` (
  `data_source_id` INT NOT NULL AUTO_INCREMENT,
  `data_source_file_path` VARCHAR(1025) NULL,
  PRIMARY KEY (`data_source_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `capstone_db`.`Project_Data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Project_Data` (
  `data_source_id` INT NOT NULL,
  `project_id` INT NOT NULL,
  INDEX `fk_Project_Data_Data1_idx` (`data_source_id` ASC) VISIBLE,
  INDEX `fk_Project_Data_Projects1_idx` (`project_id` ASC) VISIBLE,
  CONSTRAINT `fk_Project_Data_Data1`
    FOREIGN KEY (`data_source_id`)
    REFERENCES `capstone_db`.`Data` (`data_source_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Project_Data_Projects1`
    FOREIGN KEY (`project_id`)
    REFERENCES `capstone_db`.`Projects` (`project_id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `capstone_db`.`Plots`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `capstone_db`.`Plots` (
  `plot_id` INT NOT NULL AUTO_INCREMENT,
  `backtest_id` INT NOT NULL,
  `plot_type` VARCHAR(256) NOT NULL,
  `plot` BLOB,
  PRIMARY KEY (`plot_id`),
  CONSTRAINT `fk_plots_backtest_id`
    FOREIGN KEY (`backtest_id`)
    REFERENCES `capstone_db`.`Backtests` (`backtest_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



