import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


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


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status: Mapped[StockStatus] = mapped_column(Enum(StockStatus), default=StockStatus.normal)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    category: Mapped["Category | None"] = relationship("Category", back_populates="items")
