import logging
import unittest

from service import app
from service.common import status
from service.models import db, Account

class TestAccountRoutes(unittest.TestCase):

```
@classmethod
def setUpClass(cls):
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.logger.setLevel(logging.CRITICAL)
    cls.client = app.test_client()

def setUp(self):
    db.session.query(Account).delete()
    db.session.commit()

def test_index(self):
    response = self.client.get("/")
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_health(self):
    response = self.client.get("/health")
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_create_account(self):
    account = {
        "name": "John",
        "email": "john@example.com",
        "password": "secret",
    }

    response = self.client.post(
        "/accounts",
        json=account,
        content_type="application/json",
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_list_accounts(self):
    account = Account(name="Jane", email="jane@example.com", password="pass")
    account.create()

    response = self.client.get("/accounts")
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_read_account(self):
    account = Account(name="Bob", email="bob@example.com", password="pass")
    account.create()

    response = self.client.get(f"/accounts/{account.id}")
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_update_account(self):
    account = Account(name="Alice", email="alice@example.com", password="pass")
    account.create()

    updated = {
        "name": "Alice Updated",
        "email": "alice@new.com",
        "password": "new",
    }

    response = self.client.put(
        f"/accounts/{account.id}",
        json=updated,
        content_type="application/json",
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_delete_account(self):
    account = Account(name="Mark", email="mark@example.com", password="pass")
    account.create()

    response = self.client.delete(f"/accounts/{account.id}")
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
```
