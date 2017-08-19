------------- SQLite3 Dump File -------------

-- ------------------------------------------
-- Dump of "host_items"
-- ------------------------------------------

CREATE TABLE "host_items"(
	"ip_str" Text NOT NULL,
	"port" Text,
	"transport" Text,
	"product" Text,
	"devicetype" Text,
	"created" Text,
	"modified" Text,
	"asn" Text,
	"org" Text,
	"hostname" Text,
	"country_code" Text );

CREATE INDEX "index_create1" ON "host_items"( "created" );
CREATE INDEX "index_ip_str" ON "host_items"( "ip_str" );
CREATE INDEX "index_modified1" ON "host_items"( "modified" );

