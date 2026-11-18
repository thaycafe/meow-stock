import enum
import unicodedata
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.database import Base


def clean_name(name: str) -> str:
    return " ".join(name.split())


def name_key(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", clean_name(name))
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


class StockStatus(str, enum.Enum):
    normal = "normal"
    running_low = "running_low"
    out_of_stock = "out_of_stock"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    color: Mapped[str] = mapped_column(String(32), default="slate")
    items: Mapped[list["Item"]] = relationship("Item", back_populates="category")


ITEM_NAME_KEY_INDEX = "ux_items_name_key"


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (Index(ITEM_NAME_KEY_INDEX, "name_key", unique=True), {"sqlite_autoincrement": True})

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    name_key: Mapped[str] = mapped_column(String(128))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status: Mapped[StockStatus] = mapped_column(Enum(StockStatus), default=StockStatus.normal)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    category: Mapped["Category | None"] = relationship("Category", back_populates="items")

    @validates("name")
    def _sync_name_key(self, _key: str, value: str) -> str:
        value = clean_name(value)
        self.name_key = name_key(value)
        return value
