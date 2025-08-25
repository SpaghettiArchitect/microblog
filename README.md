# Microblog

This is a simple microblogging web application built with Flask, SQLite, and TailwindCSS. It allows users to create accounts, log in, and post short messages (microblogs) that are visible to all users.

## How to install and run the application?

1. Clone this repository to your local machine and `cd` into it.
2. [Install uv by Astral](https://docs.astral.sh/uv/). This is necessary to install the correct Python version and dependencies of the project.
3. [Install Node.js with npm](https://nodejs.org/en/download) on your operating system.
4. Execute the following commands in your terminal, inside of the `microblog` project directory:

```shell
# Sync the project dependencies:
# - Creates a virtual environment at /.venv
# - Downloads the correct Python version and dependencies.
uv sync

# Install all Javascript dependencies needed for the UI style (TailwindCSS, Preline, and Iconify)
cd app
npm install

# Build the CSS style file needed for the app (output.css).
npm run build

# Finally, run the Flask application
cd ..
uv run flask run
```

## How to add new functionalities?

If you want to add new functionalities to the application, you have to run it in debug mode:

```shell
uv run flask --debug run
```

Also, if you want to add new styling to some template, you need to run TailwindCSS in watch mode. This way, all new class rules added will recompile the `output.css` file. The following command should be executed in a separate terminal, inside the `app` directory:

```shell
npm run watch
```
