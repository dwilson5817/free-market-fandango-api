# Free Market Fandango

A stock market themed party where drink choices and events affect prices.

## API

This the API which runs behind the frontend.  It will connect to a MySQL/MariaDB database defined using the environment variables.  Users are authenticated using JSON Web Tokens (JWT).

The API runs as a Lambda function, invoked using API Gateway and deployed with the CDK, see the [CDK project](https://gitlab.dylanwilson.dev/free-market-fandango/cdk) for more details.

## Environment variables

The following environment variables are expected, they should mostly be self-explanatory:

- `ADMIN_PASSWORD`: admin password required to authenticate in the admin panel.
- `SECRET_KEY`: secret key used for signing JWT tokens.
- `DATABASE_HOST`: database server hostname.
- `DATABASE_PORT`: database server port.
- `DATABASE_USER`: database user.
- `DATABASE_PASS`: database password.
- `DATABASE_NAME`: database name.

## License

This application is licensed under version 3 of the GNU General Public License.  A copy of the license is available [on GitLab](https://gitlab.dylanwilson.dev/free-market-fandango/frontend/-/blob/main/LICENSE).
