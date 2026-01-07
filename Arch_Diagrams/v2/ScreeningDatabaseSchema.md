# Screening Database Schema Documentation

## Overview

This document describes the database schema for the CLM (Customer Lifecycle Management) Screening system. The schema supports journey-based screening workflows, entity management, alert processing, and audit logging for compliance screening operations through NetReveal integration.

---

## Tables

### 1. RequestResponsePayload

**Purpose:** Stores request and response payloads for screening operations, maintaining a complete audit trail of all API interactions during the screening journey.

**Description:** This table captures both inbound requests (e.g., JourneySuperGraph queries) and outbound responses for each batch. By storing complete payloads as JSON/XML.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for each payload record |
| JourneyId | Guid | | Foreign key reference to the Journey being processed. Duplicated here for query convenience from the parent ScreeningBatch . This data will come from FenX|
| ProcessId | Guid | | Unique identifier for the specific process instance. This data will come from FenX |
| BatchId | Guid | | Groups related requests/responses together. Each batch represents a cohesive unit of entities being screened |
| Payload | string | | The actual JSON or XML payload content. Contains complete request or response data for audit and debugging |
| CreatedOn | date | | Timestamp when the payload was stored in the database |
| CreatedBy | string | | User or system account that created this record (e.g., "CLM-Adaptor", "System") |
| PayloadType | string | | Discriminator field indicating payload purpose. Valid values: 'JourneySuperGraphRequest', 'JourneySuperGraphResponse', 'EntitySuperGraphRequest', 'EntitySuperGraphResponse' |

**Notes:**
- JourneyId and ProcessId are intentionally duplicated for query performance

---

### 2. ScreeningEntity

**Purpose:** Represents individual entities (persons, organizations, etc.) that are being screened as part of a journey.

**Description:** Central table for entity data during screening. Each record represents one entity with its associated metadata, current status, and screening stage. The EntityDetailsJson field contains the complete entity data retrieved from FenX for screening purposes. The EntityDetailsJson is kept as raw json as it will not be used to drive any CLM logic but converted to XML to be send to NetReveal as XML. Expanding it into fields limits the future possibility of new fields appearing in the source or destination systems.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for this screening entity record |
| BatchId | Guid | | Links this entity to a specific batch of screening operations |
| JourneyId | Guid | | The journey this entity belongs to. One journey may contain multiple entities (primary entity, counter party, related parties) |
| ProcessId | Guid | | Process instance identifier from FenX |
| ScreeningEntityId | Guid | | The actual entity ID from the source system (FenX). This is the business key for the entity being screened |
| RelationshipId | Guid | | Identifier for the relationship type between entities in a journey (e.g., primary applicant, guarantor, beneficial owner) |
| EntityType | string | | Classification of entity. Examples: 'IND' (Individual), 'ORG' (Organization), 'CORP' (Corporation) |
| BranchCode | string | FOREIGN KEY → BranchCodeOrgCodeMapping.BranchCode | Branch or brand code from the source system. Used to derive organizational unit for NetReveal screening |
| OrgCode | string | FOREIGN KEY → BranchCodeOrgCodeMapping.OrgCode | Derived organizational code used by NetReveal for screening context and configuration |
| EntityStatus | string | | Current status of the entity. Examples: 'Active', 'Inactive', 'Deleted', 'PendingVerification ?' |
| EntityDetailsJson | string | | Complete entity data in JSON format retrieved from FenX API. Contains all customer/entity attributes needed for screening |
| ScreeningStage | string | | Current stage in the screening workflow. Examples: 'Initial',  'Rework' etc |
| CreatedOn | date | | Timestamp when this entity record was created |
| CreatedBy | string | | User or system that created this record |

**Notes:**
- BrandCode is mapped to OrgCode via BrachCodeOrgCodeMapping table for multi-tenant screening configurations
- EntityDetailsJson should contain sanitized/encrypted sensitive data according to data protection policies
- Active/Inactive status is determined by checking if the entity has related entities (in case of deletions)

---

### 3. BranchCodeOrgCodeMapping

**Purpose:** Maps branch/brand codes to organizational codes for NetReveal screening configuration. 

**Description:** Reference table that maintains the mapping between source system branch codes and Banks organizational units. This enables RBAC for specific branch users to adjudicate Alerts on NetReveal
| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for each mapping record |
| BranchCode | string | FOREIGN KEY → ScreeningEntity.BrachCode | Branch or Branch code from the source system (FenX) |
| OrgCode | string | | Organizational unit code used by NetReveal for screening rules and configurations |
| CreatedOn | date | | Timestamp when this mapping was created |
| validFrom | date | | Start date when this mapping becomes effective. Supports historical tracking |
| validTo | date | | End date when this mapping expires. NULL indicates currently active mapping |

**Notes:**
- Validity (validFrom/validTo) supports organizational restructuring without losing historical contextvalidFrom`


---

### 4. ScreeningHit

**Purpose:** Records screening results from NetReveal, indicating whether an entity had a hit (match) or no-hit during screening.

**Description:** Primary screening results table that captures the outcome of NetReveal API calls. Each record represents one screening attempt for an entity. The HitNoHit flag provides quick filtering for entities requiring further review.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for this screening hit record |
| BatchId | Guid | | Links to the batch this screening belongs to |
| JourneyId | Guid | | Journey identifier for correlation and reporting |
| ProcessId | Guid | | Process instance identifier |
| ScreeningEntityId | Guid | FOREIGN KEY → ScreeningEntity.ID | Reference to the entity that was screened |
| AlertId | int | | Alert identifier returned by NetReveal. Used to query alert details and status |
| HitNoHit | bool | | Boolean flag: TRUE = Hit/Match detected, FALSE = No match found (clean screening) |
| CreatedOn | date | | Timestamp when the screening result was recorded |
| CreatedBy | string | | User or system that created this record (typically "CLM-Adaptor") |

**Notes:**
- AlertId is returned by NetReveal only when HitNoHit = TRUE
- One entity can have multiple ScreeningHit records if screened multiple times (initial, ongoing, rework)

---

### 5. ScreeningHitDetails

**Purpose:** Stores detailed information about screening alerts, including match type, match value, and processing status.

**Description:** Detail table that extends ScreeningHit with complete alert information from NetReveal. This includes the actual match data, processing workflow status etc. The AlertProcessingStatus field drives the alert resolution workflow.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for this hit detail record |
| BatchId | Guid | | Batch identifier for grouping and processing |
| JourneyId | Guid | | Journey identifier for correlation |
| ScreeningHitId | Guid | FOREIGN KEY → ScreeningHit.ID | Reference to the parent screening hit record |
| AlertId | Guid | FOREIGN KEY → ScreeningHit.AlertId | NetReveal alert identifier for tracking |
| ScreeningEntityId | Guid | FOREIGN KEY → ScreeningEntity.ID | The entity this alert pertains to |
| EntityType | string | | Type of entity (duplicated from ScreeningEntity for query convenience) |
| EntityName | string | | Name of the entity being screened (extracted from EntityDetailsJson for quick reference) |
| MatchType | string | | Type of match detected. Examples: 'Name', 'DOB', 'Address', 'TaxID', 'Passport'. Indicates which attribute triggered the alert |
| MatchValue | string | | The specific value that matched. Example: If MatchType='Name', this contains the matched name string |
| AlertProcessingStatus | string | | Current workflow status. Valid values: NULL (not processed), 'Processing' (being handled), 'Processed' (completed), 'Error' (failed) |
| HitDetailsJson | string | | Complete alert details from NetReveal in JSON format. Contains match score, watchlist name, entity details, and match confidence |
| CreatedOn | date | | Timestamp when the alert detail was recorded |
| CreatedBy | string | | User or system that created this record |

**Notes:**
- AlertProcessingStatus drives the alert workflow: NULL → Processing → Processed
- HitDetailsJson should preserve the complete NetReveal response for compliance and audit
- Consider indexing (AlertProcessingStatus, BatchId) for efficient batch processing queries
- AlertId should match between ScreeningHit and ScreeningHitDetails (consider adding CHECK constraint)

---

### 6. JourneyAlertJob

**Purpose:** Tracks scheduled jobs for processing journey alerts from NetReveal.

**Description:** Job scheduler table for the timer-triggered alert processing workflow. Maintains the last successful run timestamp to enable incremental processing of new/updated alerts. The AlertJobType discriminator supports different alert sources (NetReveal API vs. database polling).

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| JourneyAlertJobId | Guid | PRIMARY KEY | Unique identifier for this job instance |
| JobStatus | string | | Current job status. Examples: 'Idle', 'Running', 'Completed', 'Failed'. Prevents concurrent execution |
| AlertJobType | string | | Discriminator for alert source. Values: 'NetRevealAlerts' (polls NetReveal TrueHit API), 'DatabaseAlerts' (processes open alerts from DB) |
| LastRunOn | date | | Timestamp of the last successful job completion. Used as `startDateTime` parameter for incremental NetReveal API queries |

**Notes:**
- LastRunOn enables delta processing - only alerts created/updated since this timestamp are retrieved
- JobStatus should be set to 'Running' at job start and updated to 'Completed'/'Failed' at job end
- Consider adding a unique constraint on AlertJobType if only one job per type is allowed
- Failed jobs should not update LastRunOn to enable retry of the same time window

---

### 7. JourneyAlertJobRunDetails

**Purpose:** Detailed execution history for each batch processed during an alert job run.

**Description:** Audit table that records batch-level processing within an alert job. Each record represents one batch (grouped set of alerts) that was processed, including timing and status. Enables granular troubleshooting and progress tracking for long-running jobs.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for this run detail record |
| JourneyAlertJobId | Guid | FOREIGN KEY → JourneyAlertJob.JourneyAlertJobId | Links to the parent job that processed this batch |
| BatchId | Guid | | The batch identifier that was processed in this job run |
| BatchProcessingStatus | string | | Status of batch processing. Values: 'Pending', 'Processing', 'Completed', 'Failed', 'Skipped' |
| StartedOn | date | | Timestamp when batch processing began |
| CompletedOn | date | | Timestamp when batch processing finished. NULL if still in progress or failed |

**Notes:**
- One JourneyAlertJob can have multiple JourneyAlertJobRunDetails (one per batch)
- CompletedOn - StartedOn gives the processing duration for performance monitoring
- BatchProcessingStatus enables retry logic for failed batches without reprocessing successful ones
- Consider adding index on (JourneyAlertJobId, BatchProcessingStatus) for job monitoring queries

---

### 8. AuditLog

**Purpose:** Comprehensive audit trail for all API interactions, errors, and system events.

**Description:** Central logging table that captures all inbound and outbound API calls with complete request/response payloads, timing, and error details. Critical for debugging, compliance auditing, and performance analysis. Supports correlation with ErrorCodes for standardized error reporting.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for each audit log entry |
| ErrorCode | Guid | FOREIGN KEY → ErrorCodes.ID | Reference to standardized error code (NULL if successful operation) |
| APIEndpoint | string | | Full API endpoint URL or path. Example: '/api/association/root/{entityId}/journey/{journeyId}' |
| HttpMethod | string | | HTTP verb used. Values: 'GET', 'POST', 'PUT', 'DELETE', 'PATCH' |
| APIName | string | | Friendly name for the API. Examples: 'FenX SuperGraph', 'NetReveal TrueHit API', 'FenX Receptor API' |
| Direction | string | | Traffic direction. Values: 'Inbound' (received by CLM-Adaptor), 'Outbound' (sent from CLM-Adaptor to external system) |
| RequestDate | date | | Timestamp when the API request was initiated |
| RequestPayload | string | | Complete request payload (JSON/XML). Consider encryption for sensitive data |
| ResponseDate | date | | Timestamp when the API response was received |
| ResponsePayload | string | | Complete response payload (JSON/XML). Consider encryption for sensitive data |
| HttpStatusCode | int | | HTTP status code. Examples: 200 (OK), 400 (Bad Request), 500 (Internal Server Error) |
| ErrorResponse | string | | Error details if HttpStatusCode indicates failure. May contain stack traces or error messages |
| CreatedOn | date | | Timestamp when this audit record was written to the database |
| CreatedBy | string | | User or system that created this record (typically service account or system process) |

**Notes:**
- ResponseDate - RequestDate gives the API latency for performance monitoring
- Consider data retention policies - this table can grow very large
- Sensitive data in payloads should be masked or encrypted (PII, credentials, etc.)
- Index recommendations: (APIName, RequestDate), (HttpStatusCode, RequestDate), (ErrorCode)
- Direction field enables filtering for integration monitoring (track outbound vs inbound failures)

---

### 9. ErrorCodes

**Purpose:** Reference table for standardized error codes, messages, and descriptions used throughout the system.

**Description:** Master error code catalog that enables consistent error handling and reporting across all system components. Each error code includes HTTP status code mapping, human-readable reason, and detailed description for documentation and troubleshooting.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| ID | Guid | PRIMARY KEY | Unique identifier for this error code |
| ErrorCode | string | UNIQUE | Standardized error code identifier. Examples: 'CLM-001', 'CLM-002', 'NR-TIMEOUT-001'. Should follow organizational naming convention |
| StatusCode | int | | HTTP status code associated with this error. Examples: 400 (client error), 500 (server error), 503 (service unavailable) |
| Reason | string | | Short reason phrase for the error. Examples: 'Invalid Payload', 'Timeout', 'Unauthorized', 'Resource Not Found' |
| Message | string | | User-facing error message. Should be clear and actionable. Example: 'The request payload is missing required field: JourneyId' |
| Description | string | | Detailed technical description for developers and support teams. Includes troubleshooting guidance and resolution steps |
| CreatedOn | date | | Timestamp when this error code was added to the catalog |
| CreatedBy | string | | User who created this error code definition |

**Notes:**
- ErrorCode should be unique and follow a consistent naming pattern (prefix-category-number)
- This is a relatively static reference table - changes should go through change control
- Consider categorizing errors: Validation (400s), Business Logic (422), Integration (503), System (500)
- Message field should be internationalization-ready if multi-language support is needed
- Consider adding Severity field (Low, Medium, High, Critical) for alerting and SLA tracking

---

## Entity Relationships

### Primary Relationships

1. **ScreeningEntity → ScreeningHit** (One-to-Many)
   - One entity can have multiple screening hits across different screening attempts
   - FK: `ScreeningHit.ScreeningEntityId` → `ScreeningEntity.ID`

2. **ScreeningHit → ScreeningHitDetails** (One-to-One)
   - Each screening hit has one corresponding detail record with match information
   - FK: `ScreeningHitDetails.ScreeningHitId` → `ScreeningHit.ID`

3. **BrachCodeOrgCodeMapping → ScreeningEntity** (One-to-Many)
   - One branch code mapping can be used by multiple entities
   - FK: `ScreeningEntity.BranchCode` → `BrachCodeOrgCodeMapping.BranchCode`

4. **JourneyAlertJob → JourneyAlertJobRunDetails** (One-to-Many)
   - One job can process multiple batches, creating multiple run detail records
   - FK: `JourneyAlertJobRunDetails.JourneyAlertJobId` → `JourneyAlertJob.JourneyAlertJobId`

5. **ErrorCodes → AuditLog** (One-to-Many)
   - One error code can be referenced by multiple audit log entries
   - FK: `AuditLog.ErrorCode` → `ErrorCodes.ID`

### Correlation Relationships (via BatchId)

These relationships are maintained through common BatchId values rather than explicit foreign keys:

1. **RequestResponsePayload ↔ ScreeningEntity**
   - Correlated by: `BatchId`
   - Enables retrieval of original request/response for entities in a batch

2. **RequestResponsePayload ↔ ScreeningHit**
   - Correlated by: `BatchId`
   - Links screening results back to the original API calls

---

## Key Design Patterns

### 1. Batch Processing
- **BatchId** appears in multiple tables to enable grouped processing
- All entities and their screening results for a single request are grouped by BatchId
- Enables atomic operations and rollback capabilities

### 2. Journey Tracking
- **JourneyId** is propagated across all tables for end-to-end traceability
- Supports journey-level reporting and analytics
- Enables correlation of all activities for a customer journey

### 3. Process Instance Tracking
- **ProcessId** enables tracking of multiple processing attempts for the same journey
- Supports retry scenarios and reprocessing without data loss
- Useful for debugging failed processes

### 4. Temporal Validity
- **BrachCodeOrgCodeMapping** uses `validFrom`/`validTo` for temporal tracking
- Supports historical analysis and organizational changes
- Consider applying this pattern to other tables if audit history is required

### 5. Payload Preservation
- JSON/XML payloads are stored as strings for complete audit trail
- Enables debugging, replay, and compliance requirements
- Consider compression or archival strategy for large payloads

---

## Indexing Recommendations

### High-Priority Indexes

```sql
-- Batch processing queries
CREATE INDEX IX_ScreeningEntity_BatchId ON ScreeningEntity(BatchId);
CREATE INDEX IX_ScreeningHit_BatchId ON ScreeningHit(BatchId);
CREATE INDEX IX_ScreeningHitDetails_BatchId ON ScreeningHitDetails(BatchId);

-- Journey-level queries
CREATE INDEX IX_ScreeningEntity_JourneyId ON ScreeningEntity(JourneyId);
CREATE INDEX IX_ScreeningHit_JourneyId_HitNoHit ON ScreeningHit(JourneyId, HitNoHit);

-- Alert processing workflow
CREATE INDEX IX_ScreeningHitDetails_AlertProcessingStatus_BatchId 
  ON ScreeningHitDetails(AlertProcessingStatus, BatchId);

-- Audit and monitoring
CREATE INDEX IX_AuditLog_APIName_RequestDate ON AuditLog(APIName, RequestDate);
CREATE INDEX IX_AuditLog_HttpStatusCode_RequestDate ON AuditLog(HttpStatusCode, RequestDate);

-- Job scheduling
CREATE INDEX IX_JourneyAlertJobRunDetails_JobId_Status 
  ON JourneyAlertJobRunDetails(JourneyAlertJobId, BatchProcessingStatus);
```

---

## Data Retention Considerations

1. **AuditLog**: Consider partitioning by RequestDate and archiving records older than regulatory retention period (e.g., 7 years)

2. **RequestResponsePayload**: Large text fields - consider blob storage or compression for payloads >1MB

3. **ScreeningHitDetails**: HitDetailsJson may contain large NetReveal responses - monitor table size

4. **JourneyAlertJobRunDetails**: Can grow quickly - archive completed runs older than 90 days to operational archive table

---

## Security Considerations

1. **PII/Sensitive Data**: 
   - EntityDetailsJson, HitDetailsJson, RequestPayload, ResponsePayload contain sensitive data
   - Implement column-level encryption or tokenization
   - Consider field-level access controls

2. **Audit Requirements**:
   - AuditLog provides complete audit trail for compliance
   - Ensure immutability (no updates/deletes, only inserts)
   - Consider append-only table or temporal tables

3. **Data Masking**:
   - Implement data masking for non-production environments
   - Mask EntityName, MatchValue, and payload fields in lower environments

---

## Change Log

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-01-07 | System | Initial schema documentation |

---

## Glossary

- **Journey**: A customer lifecycle process (e.g., onboarding, loan application) that requires screening
- **Entity**: A person or organization being screened (customer, beneficial owner, related party)
- **Batch**: A grouped set of entities processed together in one screening operation
- **Hit**: A positive match found during screening against watchlists
- **No-Hit**: Clean screening result with no matches found
- **TrueHit API**: NetReveal API for retrieving alert status updates
- **Receptor API**: FenX API for updating journey status based on screening results
- **OrgCode**: Organizational unit code used by NetReveal for configuration and rules
- **SuperGraph**: FenX GraphQL API for querying entity relationships and hierarchy
