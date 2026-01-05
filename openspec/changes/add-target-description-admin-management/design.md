## Context
Target descriptions are saved per user and need administrative oversight. The management UI must live within the ecommerce image generator for quick access.

## Goals / Non-Goals
- Goals:
  - Provide admin-only list, edit, and delete operations for saved target descriptions.
  - Expose user and target type context in admin listings.
  - Keep the UI lightweight and scoped to the ecommerce image generator.
- Non-Goals:
  - Bulk import/export of descriptions.
  - Full-text search or advanced filtering beyond pagination.

## Decisions
- Decision: Implement admin endpoints under `/api/v1/admin/target-descriptions` using `require_admin`.
- Decision: Use paginated list responses with `limit` and `offset` to control payload size.
- Decision: Provide inline edit and delete actions inside a modal list on the ecommerce image page.

## Risks / Trade-offs
- Admin list size may grow; pagination mitigates load but requires paging UI.
- Changes rely on existing per-user storage; if no descriptions exist, the modal is empty.

## Migration Plan
- No data migration required beyond existing tables.
- Tables are created via `Base.metadata.create_all()` at startup.

## Open Questions
- None.
