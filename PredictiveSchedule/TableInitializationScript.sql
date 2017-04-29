--this file is mostly for reference
--it describes what is in the sqliteDB
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "Establishments" (
	"EstablishmentID" DECIMAL,
	"RCodeDesc" VARCHAR,
	"EstType" VARCHAR,
	"PremiseName" VARCHAR,
	"PremiseStreet" VARCHAR,
	opening_date TIMESTAMP,
	latitude DECIMAL,
	longitude DECIMAL
);
CREATE TABLE "Violations" (
	"ODATAID" DECIMAL,
	inspection_id DECIMAL,
	weight DECIMAL,
	critical_yn BOOLEAN,
	CHECK (critical_yn IN (0, 1))
);
CREATE TABLE "Inspections" (
	inspection_id DECIMAL,
	establishment_id DECIMAL,
	inspection_date TIMESTAMP,
	type VARCHAR,
	score DECIMAL,
	criticalViolations DECIMAL,
	noncriticalViolations DECIMAL
);
CREATE TABLE "Addresses" (
	"FID" DECIMAL,
	"HOUSENO" DECIMAL,
	"DIR" VARCHAR,
	"STRNAME" VARCHAR,
	"TYPE" VARCHAR,
	"ZIPCODE" DECIMAL,
	"X" DECIMAL,
	"Y" DECIMAL
);
CREATE TABLE "ThreeOneOne" (
	service_request_id DECIMAL,
	description VARCHAR,
	service_name VARCHAR,
	longitude DECIMAL,
	latitude DECIMAL,
	requested_datetime TIMESTAMP
);
CREATE TABLE "Crime" (
	"INCIDENT_NUMBER" VARCHAR,
	"DATE_OCCURED" TIMESTAMP,
	"BLOCK_ADDRESS" VARCHAR,
	"CITY" VARCHAR,
	"ZIP_CODE" VARCHAR
);
CREATE INDEX Establishments_EstablishmentID_index ON Establishments(EstablishmentID);
CREATE INDEX Violations_inspection_id_index ON Violations(inspection_id);
CREATE INDEX Violations_ODATAID_index ON Violations(ODATAID);
CREATE INDEX Inspections_inspection_id_index ON Inspections(inspection_id);
CREATE INDEX Inspections_establishment_id_index ON Inspections(establishment_id);
CREATE INDEX Addresses_ZIPCODE_index ON Addresses(ZIPCODE);
CREATE INDEX ThreeOneOne_service_request_id_index ON ThreeOneOne(service_request_id);
CREATE INDEX Crime_INCIDENT_NUMBER_index ON Crime(INCIDENT_NUMBER);
COMMIT;
