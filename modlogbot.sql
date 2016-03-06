-- MySQL dump 10.16  Distrib 10.1.11-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: modlog
-- ------------------------------------------------------
-- Server version	10.1.11-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `insertId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `createDt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` varchar(20) DEFAULT NULL,
  `archived` tinyint(1) NOT NULL,
  `author` varchar(20) NOT NULL,
  `author_flair_css_class` varchar(255) DEFAULT NULL,
  `author_flair_text` varchar(255) DEFAULT NULL,
  `banned_by` varchar(20) DEFAULT NULL,
  `body` text NOT NULL,
  `body_html` text NOT NULL,
  `controversiality` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `created_utc` datetime NOT NULL,
  `distinguished` tinyint(1) DEFAULT NULL,
  `downs` int(11) NOT NULL,
  `edited` tinyint(1) NOT NULL,
  `fetched` datetime NOT NULL,
  `fullname` varchar(12) NOT NULL,
  `gilded` int(11) NOT NULL,
  `has_fetched` tinyint(1) NOT NULL,
  `id` varchar(10) NOT NULL,
  `is_root` tinyint(1) NOT NULL,
  `likes` int(11) DEFAULT NULL,
  `link_author` varchar(20) NOT NULL,
  `link_id` varchar(20) NOT NULL,
  `link_title` text NOT NULL,
  `link_url` text NOT NULL,
  `name` varchar(20) NOT NULL,
  `num_reports` int(11) NOT NULL,
  `over_18` tinyint(1) NOT NULL,
  `parent_id` varchar(20) NOT NULL,
  `permalink` text NOT NULL,
  `quarantine` tinyint(1) NOT NULL,
  `removal_reason` text,
  `saved` tinyint(1) NOT NULL,
  `score` int(11) NOT NULL,
  `score_hidden` tinyint(1) NOT NULL,
  `stickied` tinyint(1) NOT NULL,
  `subreddit_id` varchar(255) NOT NULL,
  `subreddit` varchar(255) NOT NULL,
  `ups` int(11) NOT NULL,
  PRIMARY KEY (`insertId`),
  UNIQUE KEY `idx_id` (`id`),
  UNIQUE KEY `idx_unique` (`fullname`)
) ENGINE=InnoDB AUTO_INCREMENT=220286 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modlog`
--

DROP TABLE IF EXISTS `modlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `modlog` (
  `insertId` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `fetched` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `action` varchar(16) NOT NULL,
  `created` datetime DEFAULT NULL,
  `description` varchar(255) NOT NULL,
  `details` varchar(255) NOT NULL,
  `fullname` int(255) NOT NULL,
  `has_fetched` tinyint(1) NOT NULL,
  `id` varchar(16) NOT NULL,
  `moderator` varchar(128) NOT NULL,
  `mod_id36` varchar(8) NOT NULL,
  `rs_id36` varchar(8) NOT NULL,
  `target_author` varchar(128) NOT NULL,
  `target_fullname` varchar(12) NOT NULL,
  `target_type` varchar(2) AS (LEFT(target_fullname,2)) VIRTUAL,
  `target_permalink` text NOT NULL,
  PRIMARY KEY (`insertId`),
  UNIQUE KEY `action` (`action`,`created`,`id`,`moderator`),
  KEY `target_author` (`target_author`),
  KEY `target_author_2` (`target_author`,`action`),
  KEY `target_fullname` (`target_fullname`)
) ENGINE=InnoDB AUTO_INCREMENT=10905502 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `modlog_comments`
--

DROP TABLE IF EXISTS `modlog_comments`;
/*!50001 DROP VIEW IF EXISTS `modlog_comments`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `modlog_comments` (
  `fetched` tinyint NOT NULL,
  `action` tinyint NOT NULL,
  `created` tinyint NOT NULL,
  `description` tinyint NOT NULL,
  `details` tinyint NOT NULL,
  `fullname` tinyint NOT NULL,
  `has_fetched` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `moderator` tinyint NOT NULL,
  `mod_id36` tinyint NOT NULL,
  `rs_id36` tinyint NOT NULL,
  `target_author` tinyint NOT NULL,
  `target_fullname` tinyint NOT NULL,
  `target_type` tinyint NOT NULL,
  `target_permalink` tinyint NOT NULL,
  `body` tinyint NOT NULL,
  `is_root` tinyint NOT NULL,
  `parent_id` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `modlog_submissions`
--

DROP TABLE IF EXISTS `modlog_submissions`;
/*!50001 DROP VIEW IF EXISTS `modlog_submissions`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `modlog_submissions` (
  `fetched` tinyint NOT NULL,
  `action` tinyint NOT NULL,
  `created` tinyint NOT NULL,
  `description` tinyint NOT NULL,
  `details` tinyint NOT NULL,
  `fullname` tinyint NOT NULL,
  `has_fetched` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `moderator` tinyint NOT NULL,
  `mod_id36` tinyint NOT NULL,
  `rs_id36` tinyint NOT NULL,
  `target_author` tinyint NOT NULL,
  `target_fullname` tinyint NOT NULL,
  `target_permalink` tinyint NOT NULL,
  `domain` tinyint NOT NULL,
  `link_flair_text` tinyint NOT NULL,
  `selftext` tinyint NOT NULL,
  `url` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `submission_old`
--

DROP TABLE IF EXISTS `submission_old`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `submission_old` (
  `insertId` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `createDt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `archived` tinyint(1) NOT NULL,
  `author` varchar(100) NOT NULL,
  `banned_by` varchar(100) NOT NULL,
  `created_utc` datetime NOT NULL,
  `distinguished` tinyint(1) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `downs` int(6) NOT NULL,
  `edited` tinyint(1) NOT NULL,
  `rfrom` varchar(255) NOT NULL,
  `from_id` varchar(255) NOT NULL,
  `from_kind` varchar(255) NOT NULL,
  `gilded` int(11) NOT NULL,
  `hidden` tinyint(1) NOT NULL,
  `hide_score` tinyint(1) NOT NULL,
  `id` varchar(255) NOT NULL,
  `is_self` tinyint(1) NOT NULL,
  `link_flair_css_class` varchar(100) NOT NULL,
  `link_flair_text` varchar(255) NOT NULL,
  `locked` tinyint(1) NOT NULL,
  `media` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `permalink` varchar(255) NOT NULL,
  `post_hint` varchar(255) NOT NULL,
  `quarantine` tinyint(1) NOT NULL,
  `removal_reason` varchar(255) NOT NULL,
  `subreddit_id` varchar(16) NOT NULL,
  `title` text NOT NULL,
  `ups` int(11) NOT NULL,
  `upvote_ratio` decimal(11,0) NOT NULL,
  `url` varchar(255) NOT NULL,
  `self_text` text NOT NULL,
  PRIMARY KEY (`insertId`),
  UNIQUE KEY `permalink` (`permalink`)
) ENGINE=InnoDB AUTO_INCREMENT=2983 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `submissions`
--

DROP TABLE IF EXISTS `submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `submissions` (
  `insertId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `createDt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` varchar(20) DEFAULT NULL,
  `archived` tinyint(1) NOT NULL,
  `author` varchar(20) NOT NULL,
  `author_flair_css_class` varchar(255) DEFAULT NULL,
  `author_flair_text` varchar(255) DEFAULT NULL,
  `banned_by` varchar(20) DEFAULT NULL,
  `clicked` tinyint(1) NOT NULL,
  `created` datetime NOT NULL,
  `created_utc` datetime NOT NULL,
  `distinguished` tinyint(1) DEFAULT NULL,
  `domain` text NOT NULL,
  `downs` int(11) DEFAULT NULL,
  `edited` datetime DEFAULT NULL,
  `rfrom` varchar(20) DEFAULT NULL,
  `from_id` varchar(20) DEFAULT NULL,
  `from_kind` int(11) DEFAULT NULL,
  `fullname` varchar(20) NOT NULL,
  `gilded` int(11) NOT NULL,
  `has_fetched` tinyint(1) NOT NULL,
  `hidden` tinyint(1) NOT NULL,
  `hide_score` tinyint(1) NOT NULL,
  `id` varchar(10) NOT NULL,
  `is_self` tinyint(1) NOT NULL,
  `likes` int(11) DEFAULT NULL,
  `link_flair_css_class` varchar(255) DEFAULT NULL,
  `link_flair_text` varchar(255) DEFAULT NULL,
  `locked` tinyint(1) NOT NULL,
  `name` varchar(20) NOT NULL,
  `over_18` tinyint(1) NOT NULL,
  `permalink` text NOT NULL,
  `post_hint` varchar(255) DEFAULT NULL,
  `quarantine` tinyint(1) NOT NULL,
  `removal_reason` text,
  `saved` tinyint(1) NOT NULL,
  `score` int(11) NOT NULL,
  `selftext` text,
  `selftext_html` text,
  `short_link` varchar(255) NOT NULL,
  `stickied` tinyint(1) DEFAULT NULL,
  `subreddit` varchar(255) NOT NULL,
  `subreddit_id` varchar(20) NOT NULL,
  `title` text NOT NULL,
  `ups` int(11) NOT NULL,
  `url` text NOT NULL,
  PRIMARY KEY (`insertId`),
  UNIQUE KEY `fullname` (`fullname`),
  KEY `idx_created_utc` (`created_utc`)
) ENGINE=InnoDB AUTO_INCREMENT=195747 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'modlog'
--
/*!50003 DROP FUNCTION IF EXISTS `GetDomainFromFullName` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetDomainFromFullName`(`id` varchar(12)) RETURNS varchar(255) CHARSET utf8
    READS SQL DATA
    DETERMINISTIC
BEGIN
  DECLARE q VARCHAR(255);
	SELECT domain INTO q FROM submissions WHERE fullname = id;

	RETURN q;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetActionCountByDomain` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetActionCountByDomain`(IN `domain` VARCHAR(255))
    READS SQL DATA
    DETERMINISTIC
SELECT DISTINCT 
action,
count(*) AS cnt,
 (
      SELECT created FROM modlog_submissions WHERE modlog_submissions.domain = domain AND `ACTION` IN('removelink',
  'approvelink') ORDER BY created ASC LIMIT 1
  ) AS 'Oldest',
  (
      SELECT created FROM modlog_submissions WHERE modlog_submissions.domain = domain AND `ACTION` IN('removelink',
  'approvelink') ORDER BY created DESC LIMIT 1
  ) AS 'Newest'
FROM
modlog_submissions
WHERE
modlog_submissions.domain = domain
AND action IN ('removelink', 'approvelink')
GROUP BY
domain,
action
ORDER BY
modlog_submissions.domain,
cnt DESC ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `modlog_comments`
--

/*!50001 DROP TABLE IF EXISTS `modlog_comments`*/;
/*!50001 DROP VIEW IF EXISTS `modlog_comments`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `modlog_comments` AS select `modlog`.`fetched` AS `fetched`,`modlog`.`action` AS `action`,`modlog`.`created` AS `created`,`modlog`.`description` AS `description`,`modlog`.`details` AS `details`,`modlog`.`fullname` AS `fullname`,`modlog`.`has_fetched` AS `has_fetched`,`modlog`.`id` AS `id`,`modlog`.`moderator` AS `moderator`,`modlog`.`mod_id36` AS `mod_id36`,`modlog`.`rs_id36` AS `rs_id36`,`modlog`.`target_author` AS `target_author`,`modlog`.`target_fullname` AS `target_fullname`,`modlog`.`target_type` AS `target_type`,`modlog`.`target_permalink` AS `target_permalink`,`comments`.`body` AS `body`,`comments`.`is_root` AS `is_root`,`comments`.`parent_id` AS `parent_id` from (`comments` join `modlog` on((`comments`.`fullname` = `modlog`.`fullname`))) where (`modlog`.`target_type` = 't1') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `modlog_submissions`
--

/*!50001 DROP TABLE IF EXISTS `modlog_submissions`*/;
/*!50001 DROP VIEW IF EXISTS `modlog_submissions`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `modlog_submissions` AS select `modlog`.`fetched` AS `fetched`,`modlog`.`action` AS `action`,`modlog`.`created` AS `created`,`modlog`.`description` AS `description`,`modlog`.`details` AS `details`,`modlog`.`fullname` AS `fullname`,`modlog`.`has_fetched` AS `has_fetched`,`modlog`.`id` AS `id`,`modlog`.`moderator` AS `moderator`,`modlog`.`mod_id36` AS `mod_id36`,`modlog`.`rs_id36` AS `rs_id36`,`modlog`.`target_author` AS `target_author`,`modlog`.`target_fullname` AS `target_fullname`,`modlog`.`target_permalink` AS `target_permalink`,`submissions`.`domain` AS `domain`,`submissions`.`link_flair_text` AS `link_flair_text`,`submissions`.`selftext` AS `selftext`,`submissions`.`url` AS `url` from (`modlog` join `submissions` on((`modlog`.`target_fullname` = `submissions`.`fullname`))) where (`modlog`.`target_type` = 't3') order by `modlog`.`created` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-03-06 19:37:04
