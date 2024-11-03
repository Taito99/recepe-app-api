```markdown
# API Documentation

This repository provides an API for managing users, recipes, ingredients, and tags. It uses JSON Web Tokens (JWT) and token-based authentication to secure endpoints. This documentation explains the available API endpoints and the data they handle.

## Requirements

- Python 3.x
- Django and Django REST Framework
- drf-spectacular for OpenAPI schema generation

## Authentication

The API uses two types of authentication:
- **JWT Authentication** for most endpoints
- **Token Authentication** for user-related endpoints

Include your token in the `Authorization` header for each request:

```bash
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### API Schema

- **GET** `/api/schema/`: Retrieve the OpenAPI schema for this API. Format can be selected via content negotiation.
  - **Query Parameters**:
    - `format`: Choose between `json` or `yaml`
    - `lang`: Set a language preference (e.g., `en`, `es`, `fr`)

### User Endpoints

#### Create a User

- **POST** `/api/user/create/`: Create a new user.
  - **Request Body**:
    - `email`: User's email
    - `password`: User's password
    - `name`: User's name

#### Manage the Authenticated User

- **GET** `/api/user/me/`: Retrieve the authenticated user's details.
- **PUT** `/api/user/me/`: Update the authenticated user's details.
- **PATCH** `/api/user/me/`: Partially update the authenticated user's details.

#### Authentication

- **POST** `/api/user/token/`: Generate a JWT token for the user.
- **POST** `/api/user/token/refresh/`: Refresh the JWT access token.

### Recipe Endpoints

#### List and Create Recipes

- **GET** `/api/user/recipes/`: Retrieve a list of recipes.
  - **Query Parameters**:
    - `tags`: Comma-separated list of tag IDs to filter by
    - `ingredients`: Comma-separated list of ingredient IDs to filter by
- **POST** `/api/user/recipes/`: Create a new recipe.
  - **Request Body**:
    - `title`: Name of the recipe
    - `time_minutes`: Preparation time in minutes
    - `price`: Cost of the recipe
    - `link`: Optional link to the recipe
    - `tags`: List of tag IDs
    - `ingredients`: List of ingredient IDs

#### Recipe Details

- **GET** `/api/user/recipes/{id}/`: Retrieve details of a specific recipe.
- **PUT** `/api/user/recipes/{id}/`: Update details of a specific recipe.
- **PATCH** `/api/user/recipes/{id}/`: Partially update a specific recipe.
- **DELETE** `/api/user/recipes/{id}/`: Delete a specific recipe.

#### Upload Recipe Image

- **POST** `/api/user/recipes/{id}/upload-image/`: Upload an image for a specific recipe.

### Ingredient Endpoints

#### List and Create Ingredients

- **GET** `/api/user/ingredients/`: Retrieve a list of ingredients.
  - **Query Parameters**:
    - `assigned_only`: Filter by recipes with assigned ingredients (`0` or `1`)
- **POST** `/api/user/ingredients/`: Create a new ingredient.
  - **Request Body**:
    - `name`: Name of the ingredient

#### Ingredient Details

- **GET** `/api/user/ingredients/{id}/`: Retrieve details of a specific ingredient.
- **PUT** `/api/user/ingredients/{id}/`: Update details of a specific ingredient.
- **PATCH** `/api/user/ingredients/{id}/`: Partially update a specific ingredient.
- **DELETE** `/api/user/ingredients/{id}/`: Delete a specific ingredient.

### Tag Endpoints

#### List and Create Tags

- **GET** `/api/user/tags/`: Retrieve a list of tags.
  - **Query Parameters**:
    - `assigned_only`: Filter by recipes with assigned tags (`0` or `1`)
- **POST** `/api/user/tags/`: Create a new tag.
  - **Request Body**:
    - `name`: Name of the tag

#### Tag Details

- **GET** `/api/user/tags/{id}/`: Retrieve details of a specific tag.
- **PUT** `/api/user/tags/{id}/`: Update details of a specific tag.
- **PATCH** `/api/user/tags/{id}/`: Partially update a specific tag.
- **DELETE** `/api/user/tags/{id}/`: Delete a specific tag.

## Models and Schemas

- **User**: Contains `email`, `password`, and `name`.
- **Recipe**: Contains `title`, `time_minutes`, `price`, `link`, `tags`, and `ingredients`.
- **Ingredient**: Contains `name` and `id`.
- **Tag**: Contains `name` and `id`.
- **AuthToken**: Contains JWT token information.
- **TokenRefresh**: Contains refresh token for generating a new JWT.

## Example Request with JWT

Here's an example request to retrieve a list of recipes with authentication:

```bash
curl -X GET "http://localhost:8000/api/user/recipes/" -H "Authorization: Bearer <your_jwt_token>"
```

## License

This project is licensed under the MIT License.
```

This `README.md` file provides a structured overview of the API with clear explanations of each endpoint and model, helping users understand how to interact with the API.