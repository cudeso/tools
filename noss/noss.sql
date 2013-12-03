/*
 * noss - NMAP Open Service Scan
 * Koen Van Impe on 2013-12-01 - koen dot vanimpe at cudeso dot be
 */

DROP TABLE IF EXISTS hosts;

CREATE TABLE IF NOT EXISTS hosts (
    session			INTEGER NOT NULL,
    ip          VARCHAR(16) NOT NULL,
    hostname    VARCHAR(129),
    protocol    VARCHAR(5) DEFAULT 'ipv4',
    starttime   VARCHAR(10) NOT NULL,
    endtime     VARCHAR(10) NOT NULL,
    PRIMARY KEY (ip, session)
);

DROP TABLE IF EXISTS ports;

CREATE TABLE IF NOT EXISTS ports (
    session			    INTEGER  NOT NULL,	
    ip              VARCHAR(16) NOT NULL,
    portid          INTEGER NOT NULL,
    protocol        VARCHAR(4) NOT NULL,
    service_name    VARCHAR(129),
    service_product VARCHAR(129),
    service_version VARCHAR(129), 
    service_extra   VARCHAR(129),
    script_id       VARCHAR(129),
    script_output   VARCHAR(129),
    state           VARCHAR(33) DEFAULT 'closed',
    PRIMARY KEY (ip, portid, protocol, session),
    CONSTRAINT fk_ports_hosts FOREIGN KEY (ip, session) REFERENCES hosts(ip, session) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS fki_ports_hosts_ip
BEFORE INSERT ON ports
FOR EACH ROW BEGIN
    SELECT CASE
        WHEN ((SELECT ip FROM hosts WHERE ip = NEW.ip ) IS NULL)
        THEN RAISE(ABORT, 'insert on table "ports" violates foreign key constraint "fk_ports_hosts"')
    END;
END;

CREATE TRIGGER IF NOT EXISTS fku_ports_hosts_ip
BEFORE UPDATE ON ports
FOR EACH ROW BEGIN
    SELECT CASE
        WHEN ((SELECT ip FROM hosts WHERE ip = NEW.ip AND session = NEW.session) IS NULL)
        THEN RAISE(ABORT, 'update on table "ports" violates foreign key constraint "fk_ports_hosts"')
    END;
END;

CREATE TRIGGER IF NOT EXISTS fkd_ports_hosts_ip
BEFORE DELETE ON hosts
FOR EACH ROW BEGIN
    DELETE from ports WHERE ip = OLD.ip AND session = OLD.session;
END;

/* EOF */
