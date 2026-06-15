"""Proste haszowanie hasła na potrzeby projektu uczelnianego.

To nie jest mechanizm produkcyjny: SHA-256 bez soli, brak wymagań co do hasła
(dozwolone są krótkie i proste hasła). Wystarczające do demonstracji logowania.
"""

import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash
