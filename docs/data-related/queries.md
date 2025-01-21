# Database interaction logic (query builders)

/query folder
Query logic, such as fetching from the database or applying filters, is centralized in /queries.
These queries interact with models and abstract away database logic from the API layer.

Queries: Logic for Data Access and Processing
Queries encapsulate the logic for interacting with the database. They:

Use SQLAlchemy (or another ORM) to fetch, filter, aggregate, or manipulate data.
Abstract database logic away from the API layer, making it reusable and testable.
Key Points About Queries:
Queries are backend-only and unrelated to REST.
They operate directly on models/ (e.g., SQLAlchemy models) to fetch or process data.
API routes often call queries after validating input using schemas.
