"""Fixtures for API tests; all Supabase calls stay in memory."""

from copy import deepcopy

import pytest

import app as app_module
from security import hash_password


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, client, table):
        self.client = client
        self.table_name = table
        self.filters = {}
        self.limit_count = None
        self.operation = "select"
        self.payload = None

    def select(self, _columns):
        self.operation = "select"
        return self

    def eq(self, column, value):
        self.filters[column] = value
        return self

    def limit(self, count):
        self.limit_count = count
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def execute(self):
        rows = self.client.tables[self.table_name]
        if self.operation == "insert":
            rows.append(deepcopy(self.payload))
            return FakeResponse([self.payload])

        matches = [
            row for row in rows
            if all(row.get(column) == value for column, value in self.filters.items())
        ]
        if self.limit_count is not None:
            matches = matches[:self.limit_count]
        return FakeResponse(deepcopy(matches))


class FakeSupabase:
    def __init__(self):
        self.tables = {
            "utilisateur": [
                {
                    "user_id": "usr-20041",
                    "email": "ines.moreau@demo.healthaicoach.fr",
                    "password_hash": hash_password("TestPassword!"),
                    "display_name": "Inès Moreau",
                    "role": "USER",
                    "account_status": "ACTIVE",
                },
                {
                    "user_id": "usr-20043",
                    "email": "nadia.haddad@demo.healthaicoach.fr",
                    "password_hash": hash_password("TestPassword!"),
                    "display_name": "Nadia Haddad",
                    "role": "USER",
                    "account_status": "DISABLED",
                },
                {
                    "user_id": "adm-20001",
                    "email": "karim.dupont@demo.healthaicoach.fr",
                    "password_hash": hash_password("TestAdmin!"),
                    "display_name": "Karim Dupont",
                    "role": "FUNCTIONAL_ADMIN",
                    "account_status": "ACTIVE",
                },
            ],
        }

    def table(self, name):
        return FakeQuery(self, name)


@pytest.fixture
def supabase():
    return FakeSupabase()


@pytest.fixture
def client(supabase):
    app_module.app.config["SUPABASE_CLIENT"] = supabase
    app_module.service_state["unavailable"] = False
    return app_module.app.test_client()
