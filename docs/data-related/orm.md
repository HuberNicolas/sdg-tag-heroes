# Difference Between Models and Schemas in FastAPI

https://fastapi.tiangolo.com/yo/tutorial/sql-databases/


## Models (SQLAlchemy):
- Purpose: Models represent database tables. They are used to interact with the database and perform CRUD operations (Create, Read, Update, Delete).
- Use Case: These models are directly mapped to the database tables, where each attribute corresponds to a database column. They are used when querying or manipulating data in the database.
- Example
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
```

## Schemas (Pydantic):
- Purpose: Schemas are used for data validation and serialization. They define the structure of the data expected in API requests (e.g., payloads) and responses (e.g., JSON responses).
- Use Case: Schemas validate input data (e.g., from API clients) and control what data should be returned in responses. They can filter sensitive or unnecessary data, such as excluding `hashed_password` in the API response.
- Example
```python
class UserBase(BaseModel):
    email: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
```


## When to Use Each:
- Use SQLAlchemy Models:
    - When interacting directly with the database.
    - For performing queries, updates, and inserting data into tables.
- Use Pydantic Schemas:
  - For validating and serializing data sent or received by the API.
  - When defining the structure of API requests (e.g., data from client) and responses (e.g., data sent back to client).
  - To prevent exposing sensitive data (e.g., hashed passwords, internal IDs) or to control what data is returned in an API response.

## Is It Recommended to Use Both?
  Yes, it's highly recommended to use both:
- SQLAlchemy models for database interaction.
- Pydantic schemas for data validation and serialization in API responses.

This separation ensures:

- Security: Avoid sending sensitive data to clients.
- Clean Code: Clear separation of concerns between database interaction (SQLAlchemy models) and data validation (Pydantic schemas).
- Efficiency: Pydantic ensures data is validated and serialized correctly, while SQLAlchemy efficiently manages database operations.

Conclusion:
- Models: Handle database operations (SQLAlchemy).
- Schemas: Handle API validation and serialization (Pydantic).


## How to Connect SQLAlchemy Models and Pydantic Schemas Without Adding Redundancy
The goal is to minimize redundancy while ensuring that both SQLAlchemy models (for database interaction) and Pydantic schemas (for data validation and serialization) are used efficiently. FastAPI makes this easier by supporting Pydantic’s orm_mode, which allows Pydantic to work seamlessly with SQLAlchemy models.

### 1. Using `orm_mode` to Connect SQLAlchemy Models and Pydantic Schemas
Pydantic's `orm_mode` allows the schema to accept SQLAlchemy models as input. This way, you can avoid duplicating field definitions between SQLAlchemy models and Pydantic schemas while still using Pydantic for data validation and serialization.

Here’s how to structure this connection:

#### SQLAlchemy Model (Database Layer)
This model represents the database schema and is used to perform queries and updates.

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=True)
    
    # Relationship to other tables
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Reverse relationship
    owner = relationship("User", back_populates="items")
```

#### Pydantic Schema with `orm_mode` (Validation and Serialization Layer)
Use Pydantic schemas for serialization and validation. The key here is `orm_mode=True, which allows the schema to work directly with the SQLAlchemy model objects.

### 2. How `orm_mode` Minimizes Redundancy
- SQLAlchemy models handle the database interaction, including querying and modifying data.
- Pydantic schemas focus on validating and controlling what is sent to and from the API.
- By enabling `orm_mode` in Pydantic schemas, you can directly pass SQLAlchemy models to Pydantic without needing to convert them manually.

For example, when you return a `User` model from the database in a FastAPI route, the Pydantic schema will automatically convert it into the `UserResponse` schema (with the exact fields specified in the schema) without the need for redundant data mappings.

### 3. Example Endpoint Connecting SQLAlchemy Models and Pydantic Schemas

Here’s how you connect them in a FastAPI route:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .models import User, Item  # SQLAlchemy models
from .schemas import UserResponse  # Pydantic schema
from .database import get_db  # Dependency for database session

app = FastAPI()

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user  # This SQLAlchemy model is automatically converted to a Pydantic schema
```

### 4. How It Works:
Fetching Data: The FastAPI route queries the database for a `User` using the SQLAlchemy model.
Serialization: Thanks to `orm_mode=True` in the Pydantic `UserResponse` schema, the SQLAlchemy model object is automatically converted into a Pydantic model when returned.
Minimal Redundancy: You don’t need to manually create dictionaries or map SQLAlchemy fields to Pydantic fields—`orm_mode` takes care of that.

### 5. Benefits of This Approach:
Separation of Concerns: SQLAlchemy models handle database logic, while Pydantic schemas handle validation and serialization.
Code Reusability: Both SQLAlchemy models and Pydantic schemas can be reused in different parts of the application (e.g., models for queries, schemas for API responses).
Avoid Redundancy: You avoid duplicating field definitions. You define database-specific fields in the SQLAlchemy model, and with `orm_mode`, Pydantic can read from that without extra mappings.
Security: Pydantic schemas ensure that sensitive fields (like `hashed_password`) are not exposed in API responses.

### 6. Advanced Use Case: Partial Updates
If you need to support partial updates (like updating only some fields), you can use separate Pydantic schemas, such as UserUpdate, which can make certain fields optional:

```python
class UserUpdate(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True
```

This schema can be used to validate data in `PATCH` or `PUT` requests, avoiding redundancy and keeping validation logic clean.

## Conclusion:
- SQLAlchemy models interact with the database and define the schema for the tables.
- Pydantic schemas handle API validation and data serialization, with minimal redundancy thanks to Pydantic’s `orm_mode`.
- By following this approach, you ensure a clean, state-of-the-art architecture that minimizes redundancy while maintaining clear separation between database logic and API handling.


## TypeScript Schema Generation

### Prerequisites
1. Install the `json-schema-to-typescript` package using `pnpm`:
   ```bash
   pnpm add -g json-schema-to-typescript
   ```

2. Ensure `pydantic-to-typescript` is installed via `poetry`:
   ```bash
   poetry add pydantic-to-typescript
   ```

### Generate Schemas
Run the Python script to generate TypeScript schemas:
```bash
python generate_types.py
```

The generated `.ts` files will be saved in the `types` directory.

## Models to Schemas.py to Schemas.ts

Navigate to the `pipeline` directory, activate the appropriate environment, and run the following:
```bash
python generate_types.py
```

**Note**: Not all schemas may be generated due to potential circular imports.

---
