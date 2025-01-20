# Pydantic schemas (for inputs and responses)


All validation and serialization logic (inputs and outputs) is centralized in /schemas.
A single file per feature/domain contains both input and response schemas, making it easier to find related definitions.


Schemas: Purely REST
Schemas are designed to define data contracts for the REST API. Their main purpose is:

Input Validation: Ensuring the data received in API requests (e.g., POST, PUT, query parameters) is well-formed and type-checked.
Output Serialization: Structuring data sent in API responses.
Key Points About Schemas:
Input Schema (Request): Defines what data the API can accept, like the payload for creating or updating an entity.
Response Schema: Defines the shape of the data returned to the client.
