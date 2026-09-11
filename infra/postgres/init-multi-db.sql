-- Runs automatically the first time the postgres container initializes its
-- data directory (docker-entrypoint-initdb.d convention). Creates one
-- database per microservice — this is the physical enforcement of
-- database-per-service: each service's own DATABASE_URL points at a
-- different database on this same Postgres instance.
--
-- No explicit GRANT statements are needed: this script runs as
-- $POSTGRES_USER, which the official postgres image always creates as a
-- superuser regardless of its name — so it already has full access to
-- every database created below.

CREATE DATABASE user_db;
CREATE DATABASE itinerary_db;
CREATE DATABASE recommendation_db;
