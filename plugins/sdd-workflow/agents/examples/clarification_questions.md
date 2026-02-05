# Example Questions

## Good Questions

**Data Model - User Status Nullability**

> Should the `status` field in the User model allow null values?
>
> Options:
> - A: Required field, default to "active"
> - B: Optional field, null means "unverified"
> - C: Required field, no default (must be set explicitly)
>
> Impact: Affects database schema, API validation, and error handling

**Flow - Authentication Failure Retry Policy**

> What should happen after failed authentication attempts?
>
> Options:
> - A: No limit, allow indefinite retries
> - B: Lock account after 5 failures for 15 minutes
> - C: Exponential backoff: 1s, 5s, 15s, then lock
>
> Impact: Security posture and user experience

**Integration - Payment Gateway Timeout Handling**

> How should the system handle payment gateway timeouts?
>
> Options:
> - A: Fail immediately, user must retry
> - B: Retry 3 times with exponential backoff
> - C: Mark as "pending" and poll status endpoint
>
> Impact: Payment reliability and user trust

## Questions to Avoid

**Too Vague**
> "How should we handle errors?" (Which errors? What context?)

**Already Specified**
> "Should we validate user input?" (If spec says to validate, don't ask)

**Not Implementable**
> "What's the best architecture?" (Too broad, ask about specific decisions)

**Preference-Based**
> "Do you prefer REST or GraphQL?" (Should be based on requirements, not preference)
