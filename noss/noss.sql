------------- SQLite3 Dump File -------------

-- ------------------------------------------
-- Dump of "hosts"
-- ------------------------------------------

DROP TABLE IF EXISTS "hosts";

CREATE TABLE "hosts"(
	"session" Integer NOT NULL,
	"ip" Text NOT NULL,
	"hostname" Text,
	"protocol" Text DEFAULT 'ipv4',
	"starttime" Text NOT NULL,
	"endtime" Text NOT NULL,
	"hostsCol" Text,
PRIMARY KEY ( "ip","session" ) );

CREATE TRIGGER "fkd_ports_hosts_ip"
	BEFORE DELETE
	ON "hosts"
	FOR EACH ROW
BEGIN
    DELETE from ports WHERE ip = OLD.ip AND session = OLD.session;
END;

-- ------------------------------------------
-- Dump of "ports"
-- ------------------------------------------

DROP TABLE IF EXISTS "ports";

CREATE TABLE "ports"(
	"session" Integer NOT NULL,
	"ip" Text NOT NULL,
	"portid" Integer NOT NULL,
	"protocol" Text NOT NULL,
	"service_name" Text,
	"service_product" Text,
	"service_version" Text,
	"service_extra" Text,
	"script_id" Text,
	"script_output" Text,
	"state" Text DEFAULT 'closed',
	CONSTRAINT "link_hosts_ports_0" FOREIGN KEY ( "ip","session" ) REFERENCES "hosts"( "ip","session" )
		ON DELETE Cascade
,
PRIMARY KEY ( "ip","portid","protocol","session" ) );

CREATE TRIGGER "fki_ports_hosts_ip"
	BEFORE INSERT
	ON "ports"
	FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN ((SELECT ip FROM hosts WHERE ip = NEW.ip ) IS NULL)
        THEN RAISE(ABORT, 'insert on table "ports" violates foreign key constraint "fk_ports_hosts"')
    END;
END;

CREATE TRIGGER "fku_ports_hosts_ip"
	BEFORE UPDATE
	ON "ports"
	FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN ((SELECT ip FROM hosts WHERE ip = NEW.ip AND session = NEW.session) IS NULL)
        THEN RAISE(ABORT, 'update on table "ports" violates foreign key constraint "fk_ports_hosts"')
    END;
END;

