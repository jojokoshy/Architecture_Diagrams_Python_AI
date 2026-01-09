**Rework Flow — Business Summary**

**Overview**
- Purpose: The Rework Flow handles cases where a previously processed business journey needs to be re-run (reworked). It accepts a Journey ID and uses existing draft entities to re-submit those items through the screening and alerting process so that any missing or updated results are retrieved and processed.
- Who uses it: Systems (APIs and automation) — no human interaction is required once the flow is triggered.

**Trigger & Input**
- Trigger: A Rework action is initiated (e.g., user or system requests re-evaluation for a Journey).
- Input: The flow receives a minimal payload that includes the Journey ID and related entity identifiers.

**High-level Steps**
1. Receive request: The system receives the rework request containing the Journey ID.
2. Decrypt and validate: The request payload is decrypted (using Key Vault) and validated to ensure required fields are present.
3. Acknowledge receipt: If the request is valid, the system immediately returns an HTTP 202 (Accepted) to the requester and continues processing asynchronously.
4. Gather entities: The flow collects the set of entities associated to that Journey (the current draft entities that should be reprocessed).
5. For each entity:
   - Check whether the entity still exists in the external system (some entities may have been deleted since the original run).
   - Retrieve the full entity details for the current draft version.
   - Convert or prepare the entity data into the format required for screening.
   - Call the screening engine (NetReveal) to perform screening for that entity.
   - Capture the screening result (for example, whether an alert or match was produced).
   - If the screening call returns no new alerts, the flow attempts to find previously generated alerts for the same customer and timeframe so the system can surface existing alert information back to the Journey.
6. Continue looping through all entities until processing completes.

**Decisions & Branches (Business view)**
- Is the request valid? If no, the system responds with a Bad Request and stops. If yes, processing continues in the background.
- Is the entity deleted? Deleted entities are marked as inactive and not screened.
- Did screening produce alerts? If yes, alerts are saved and associated to the Journey; if no, the system tries to fetch prior alerts for the same customer/timeframe.

**Notifications & Outputs**
- Immediate: The requester receives an HTTP 202 to confirm work has started.
- Final: The rework does not send a synchronous response back to the requester; instead, the resulting alert data and processing status are persisted and are available to downstream systems or the Supergraph API for retrieval.

**Error Handling (Business view)**
- Errors are caught centrally: failures are logged and an error notification is sent to a receptor API for monitoring and support.
- The flow isolates errors per-entity so processing can continue for other entities even if one fails.

**Key Systems Involved**
- CLM-Adaptor: Orchestrates the rework flow and coordinates calls to other systems.
- Key Vault: Used to securely store and provide decryption keys for incoming requests.
- Supergraph / FenX: Provides the list of entities and returns entity details and associations.
- NetReveal (screening engine): Performs the screening and returns alert/match results.

**When to use Rework Flow (Examples)**
- A Journey needs re-evaluation because an upstream data correction was applied.
- A previous screening run did not return expected alerts and the business requires a retry using the same draft entities.
- Regulators or auditors request a re-run of a specific Journey to verify results.

**Notes / Business Considerations**
- The flow operates asynchronously to ensure responsive APIs: callers receive quick acknowledgment while potentially long-running screening work continues in the background.
- The flow intentionally works with the current "draft" entity versions so rework uses the same data state as would be seen by normal processing.
- For privacy and security, payload decryption and access to screening services are performed using secured keys and controlled API calls.

If you want this converted into a one-page SLA-friendly diagram or a short runbook for operations, I can produce that next.
