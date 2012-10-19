-- MySQL dump 10.13  Distrib 5.1.61, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: yasound
-- ------------------------------------------------------
-- Server version	5.1.61-0+squeeze1

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
-- Table structure for table `yasound_album`
--

DROP TABLE IF EXISTS `yasound_album`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yasound_album` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lastfm_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `musicbrainz_id` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_simplified` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `cover_filename` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lastfm_id` (`lastfm_id`)
) ENGINE=MyISAM AUTO_INCREMENT=240216 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yasound_artist`
--

DROP TABLE IF EXISTS `yasound_artist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yasound_artist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `echonest_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `lastfm_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `musicbrainz_id` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_simplified` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `echonest_id` (`echonest_id`),
  KEY `lastfm_id_idx` (`lastfm_id`)
) ENGINE=MyISAM AUTO_INCREMENT=95656 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yasound_genre`
--

DROP TABLE IF EXISTS `yasound_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yasound_genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `name_canonical` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=469 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yasound_song`
--

DROP TABLE IF EXISTS `yasound_song`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yasound_song` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `artist_id` int(11) DEFAULT NULL,
  `album_id` int(11) DEFAULT NULL,
  `echonest_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastfm_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastfm_fingerprint_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `musicbrainz_id` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  `filename` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `filesize` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name_simplified` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `artist_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `artist_name_simplified` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `album_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `album_name_simplified` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration` int(11) NOT NULL,
  `danceability` decimal(10,2) DEFAULT NULL,
  `loudness` decimal(10,2) DEFAULT NULL,
  `energy` decimal(10,2) DEFAULT NULL,
  `tempo` decimal(10,2) DEFAULT NULL,
  `tonality_mode` smallint(6) DEFAULT NULL,
  `tonality_key` smallint(6) DEFAULT NULL,
  `fingerprint` longtext COLLATE utf8_unicode_ci,
  `fingerprint_hash` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `echoprint_version` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  `publish_at` datetime DEFAULT NULL,
  `published` tinyint(1) NOT NULL,
  `locked` tinyint(1) NOT NULL,
  `allowed_countries` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `comment` longtext COLLATE utf8_unicode_ci,
  `cover_filename` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `quality` smallint(6) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `privacy` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `yasound_song_e995513f` (`artist_id`),
  KEY `yasound_song_ed6c39b8` (`album_id`),
  KEY `lastfm_id_idx` (`lastfm_id`),
  KEY `echonest_id_idx` (`echonest_id`),
  KEY `name_simplified_idx` (`name_simplified`),
  KEY `artist_name_simplified_idx` (`artist_name_simplified`),
  KEY `album_name_simplified_idx` (`album_name_simplified`)
) ENGINE=MyISAM AUTO_INCREMENT=2059767 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yasound_song_genre`
--

DROP TABLE IF EXISTS `yasound_song_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yasound_song_genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `song_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `song_id` (`song_id`,`genre_id`),
  KEY `yasound_song_genre_c170b8c9` (`song_id`),
  KEY `yasound_song_genre_f8d711d0` (`genre_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1927430 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-10-19  6:35:58
