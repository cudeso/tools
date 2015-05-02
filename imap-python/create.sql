------------- SQLite3 Dump File -------------

-- ------------------------------------------
-- Dump of "headers"
-- ------------------------------------------

CREATE TABLE "headers"(
	"mailid" Integer,
	"header" Text,
	"value" Text,
	"header_stripped" Text,
	"value_stripped" Text );

CREATE INDEX "headersIdx" ON "headers"( "mailid" );

-- ------------------------------------------
-- Dump of "mails"
-- ------------------------------------------

CREATE TABLE "mails"(
	"mailid" Integer,
	"multi_part" Text,
	"number_headers" Integer,
	"content_type" Text,
	"full_length" Text,
	"md5" Text,
	"subject" Text,
	"subject_len" Integer,
	"subject_md5" Text,
	"subject_stripped_md5" Text );

CREATE INDEX "mailsIdx" ON "mails"( "mailid" );

