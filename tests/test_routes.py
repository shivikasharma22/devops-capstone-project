
# service/routes.py
"""
Routes (Controller) for the Account REST API service.
Implements CRUD endpoints and health/home checks.
"""

from flask import jsonify, request, make_response, abort, url_for
from service import app  # Flask application instance from service/__init__.py
from service.models import Account, DataValidationError
from service.common import status


######################################################################
# Utility Functions
######################################################################
def _check_content_type_json():
    """Ensure the request has JSON content type."""
    # request.is_json handles variants like "application/json; charset=utf-8"
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            description="Content-Type must be application/json",
        )


######################################################################
# Health and Root
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root endpoint for sanity check."""
    message = {
        "name": "Account REST API Service",
        "status": "OK",
        "version": "1.0",
    }
    return make_response(jsonify(message), status.HTTP_200_OK)


@app.route("/health", methods=["GET"])
def health():
    """Health probe endpoint."""
    return make_response(jsonify({"status": "OK"}), status.HTTP_200_OK)


######################################################################
# Account Collection Endpoints
######################################################################
@app.route("/accounts", methods=["POST"])
def create_account():
    """
    Create a new Account.
    Expects JSON body compatible with Account.deserialize.
    Returns:
      201 Created with the new resource and Location header.
      400 Bad Request on validation errors.
      415 Unsupported Media Type when Content-Type is not JSON.
    """
    app.logger.info("Request to create an Account")
    _check_content_type_json()

    try:
        data = request.get_json()
        account = Account()
        account.deserialize(data)
        account.create()
    except DataValidationError as err:
        abort(status.HTTP_400_BAD_REQUEST, description=str(err))

    location_url = url_for("get_accounts", account_id=account.id, _external=False)
    resp = make_response(jsonify(account.serialize()), status.HTTP_201_CREATED)
    resp.headers["Location"] = location_url
    return resp


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List Accounts.
    Optional query param: ?name=<string> to filter by name.
    Returns 200 with a JSON array.
    """
    name = request.args.get("name")
    app.logger.info("Request to list Accounts%s", f" with name={name}" if name else "")

    if name:
        accounts = Account.find_by_name(name)
    else:
        accounts = Account.all()

    results = [acct.serialize() for acct in accounts]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# Account Resource Endpoints
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id: int):
    """
    Read a single Account by id.
    Returns:
      200 with the account JSON when found
      404 when not found
    """
    app.logger.info("Processing lookup for id %s ...", account_id)
    account = Account.find(account_id)
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND,
            description=f"Account with id [{account_id}] not found.",
        )
    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id: int):
    """
    Update an existing Account by id.
    Expects JSON body compatible with Account.deserialize.
    Returns:
      200 with the updated resource
      404 if the account does not exist
      400 on validation errors
      415 if Content-Type is not JSON
    """
    app.logger.info("Request to update Account id=%s", account_id)
    _check_content_type_json()

    account = Account.find(account_id)
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND,
            description=f"Account with id [{account_id}] not found.",
        )

    try:
        data = request.get_json()
        # Ensure the instance keeps the same id
        account.deserialize(data)
        account.id = account_id
        account.update()
    except DataValidationError as err:
        abort(status.HTTP_400_BAD_REQUEST, description=str(err))

    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int):
    """
    Delete an Account by id.
    Returns:
      204 No Content (idempotent, even if already absent)
    """
    app.logger.info("Request to delete Account id=%s", account_id)
    account = Account.find(account_id)
    if account:
        account.delete()
    # Per REST best practice and common test expectations, delete is idempotent
    return make_response("", status.HTTP_204_NO_CONTENT)
