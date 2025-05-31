"""Database models for the BIN lookup application."""  # :contentReference[oaicite:0]{index=0}

from __future__ import annotations
from typing import Optional

from . import db


class Bin(db.Model):
    """Model representing a Bank Identification Number record."""

    __tablename__ = "bins"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bin: str = db.Column(db.String(6), unique=True, nullable=False)
    category: Optional[str] = db.Column(db.String(50), nullable=True)
    reloadable: Optional[str] = db.Column(db.String(50), nullable=True)
    international: Optional[str] = db.Column(db.String(50), nullable=True)
    max_balance: Optional[int] = db.Column(db.Integer, nullable=True)
    company: Optional[str] = db.Column(db.String(100), nullable=True)
    country: Optional[str] = db.Column(db.String(100), nullable=True)
    customer_service: Optional[str] = db.Column(db.String(100), nullable=True)
    distributor: Optional[str] = db.Column(db.String(100), nullable=True)
    issuer: Optional[str] = db.Column(db.String(100), nullable=True)
    type: Optional[str] = db.Column(db.String(50), nullable=True)
    website_url: Optional[str] = db.Column(db.String(200), nullable=True)

    def as_dict(self) -> dict:
        """Return a dictionary representation of the BIN record without the internal ID."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "id"
        }


class Submission(db.Model):
    """User submitted BIN corrections."""

    __tablename__ = "submissions"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bin: str = db.Column(db.String(6), nullable=False)
    category: Optional[str] = db.Column(db.String(50), nullable=True)
    reloadable: Optional[str] = db.Column(db.String(50), nullable=True)
    international: Optional[str] = db.Column(db.String(50), nullable=True)
    max_balance: Optional[int] = db.Column(db.Integer, nullable=True)
    company: Optional[str] = db.Column(db.String(100), nullable=True)
    country: Optional[str] = db.Column(db.String(100), nullable=True)
    customer_service: Optional[str] = db.Column(db.String(100), nullable=True)
    distributor: Optional[str] = db.Column(db.String(100), nullable=True)
    issuer: Optional[str] = db.Column(db.String(100), nullable=True)
    type: Optional[str] = db.Column(db.String(50), nullable=True)
    website_url: Optional[str] = db.Column(db.String(200), nullable=True)

    def as_dict(self) -> dict:
        """Return a dict representation of the submission."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "id"
        }
