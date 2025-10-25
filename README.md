# Microblog

This is a simple microblogging web application built with Flask. It allows users to create accounts, log in, and post short messages (microblogs) that are visible to all users. It also includes features such as user profiles, following other users, and searching for posts.

This project is inspired by the [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg, but has some additional features and improvements.

## How to install and run the application?

1. Clone this repository to your local machine and `cd` into it.
2. [Install uv by Astral](https://docs.astral.sh/uv/). This is necessary to install the correct Python version and dependencies for the project.
3. [Install Node.js and pnpm](https://nodejs.org/en/download) on your operating system.
4. Execute the following commands in your terminal, inside of the `microblog` project directory:

```shell
# Sync the project dependencies:
# - Creates a virtual environment at /.venv
# - Downloads the correct Python version and dependencies.
uv sync

# Install all Javascript dependencies needed for UI styling (TailwindCSS, Preline, and Iconify)
cd app
pnpm install

# Build the CSS style file needed for the app (output.css).
pnpm build

# Finally, run the Flask application
cd ..
uv run flask db upgrade # Creates the database.
uv run flask run
```

## Environment variables

The environment variables that can be set are:

- `SECRET_KEY`: The secret key for the Flask application. Should be set to a strong random value in production.
- `DATABASE_URL`: The database URL for the application. Defaults to a local SQLite database.

For email functionality, you can also set:

- `MAIL_SERVER`: The mail server address.
- `MAIL_PORT`: The mail server port.
- `MAIL_USE_TLS`: Whether to use TLS for email.
- `MAIL_USERNAME`: The username for the mail server.
- `MAIL_PASSWORD`: The password for the mail server.

For searching functionality, you can set:

- `ELASTICSEARCH_URL`: The URL of the Elasticsearch server.

For translation functionality, you can set:

- `TRANSLATION_KEY`: The API key for the translation service. Currently supports Microsoft Translator Text API.

For background task processing, you can set:

- `REDIS_URL`: The URL of the Redis server.

## API documentation

The application provides a RESTful API for accessing, creating and updating users. The following endpoints are available:

| Endpoint                    | Method | Description                              | Authenticated |
| --------------------------- | ------ | ---------------------------------------- | ------------- |
| `/api/tokens`               | POST   | Get an authentication token.             | No            |
| `/api/tokens`               | DELETE | Revoke the current authentication token. | Yes           |
| `/api/users`                | GET    | Get a list of all users.                 | Yes           |
| `/api/users/<id>`           | GET    | Get a specific user by ID.               | Yes           |
| `/api/users`                | POST   | Create a new user.                       | No            |
| `/api/users/<id>`           | PUT    | Update a specific user by ID.            | Yes           |
| `/api/users/<id>/followers` | GET    | Get followers of a specific user by ID.  | Yes           |
| `/api/users/<id>/following` | GET    | Get following of a specific user by ID.  | Yes           |

`httpie` is provided as a development dependency to test the API endpoints. For example, to work with the authentication token endpoint, you can run:

```shell
# To get a new token:
uv run http --auth <username>:<password> POST http://localhost:5000/api/tokens
# To revoke the current token:
uv run http -A bearer --auth <token> DELETE http://localhost:5000/api/tokens
```

For each request that requires authentication, you need to provide the token in the `Authorization` header using the `Bearer` scheme:

```shell
uv run http -A bearer --auth <token> GET http://localhost:5000/api/users
```

## How to add new functionality?

### Development mode

If you want to add new functionality to the application, you have to run it in debug mode:

```shell
uv run flask --debug run
```

### Styling with TailwindCSS

Also, if you want to add new styling to some template, you need to run TailwindCSS in watch mode. This way, all new class rules added will recompile the `output.css` file. The following command should be executed in a separate terminal, inside the `app` directory:

```shell
pnpm watch
```

### Translations

When new translations are added to the application (using `_()` or `_l()`), run the following to update the `messages.po` file:

```shell
uv run flask translate update
```

Then, after making the translations, compile them with:

```shell
uv run flask translate compile
```

Currently, the application supports English and Spanish languages. To add a new language, use the following command:

```shell
uv run flask translate init <lang_code>
```

Replace `<lang_code>` with the desired language code (e.g., `fr` for French).

## How to deploy the application?

### Using Docker

A `Dockerfile` is provided to build a Docker image for the application. To build and run the Docker container, execute the following commands:

```shell
# Build the Docker image
docker build -t microblog .

# Run the Docker container
docker run -d -p 5000:5000 microblog
```

The application will be accessible at `http://localhost:5000`.

You can also provide environment variables to the docker container by providing a `.env` file and using the `--env-file` option when running the container:

```shell
docker run -d -p 5000:5000 --env-file .env microblog
```
