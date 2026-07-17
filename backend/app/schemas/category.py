"""Category taxonomy — a stable machine enum with a bilingual label map.

The engine reasons over the enum key; the API emits both the key and the Arabic
label the dashboard renders. The Arabic string is NEVER a primary key.

Rule: this enum is **add-only** — never rename or renumber an existing member,
so older clients and cached results stay valid. The original 7 keys stay; the
12 spend/flow keys below mirror the Khawarizm DATA_SPEC taxonomy so the dashboard
can be seeded from the generated transactions.csv.
"""

from __future__ import annotations

from enum import Enum


class Category(str, Enum):
    # Original Midd merchant-decode categories.
    RESTAURANT = "RESTAURANT"
    FOOD_DELIVERY = "FOOD_DELIVERY"
    SHOPPING = "SHOPPING"
    GROCERY = "GROCERY"
    TELECOM = "TELECOM"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"
    # Khawarizm DATA_SPEC taxonomy (generated dataset).
    FOOD = "FOOD"
    GROCERIES = "GROCERIES"
    TRANSPORT = "TRANSPORT"
    BILLS = "BILLS"
    HEALTH = "HEALTH"
    ENTERTAINMENT = "ENTERTAINMENT"
    TRAVEL = "TRAVEL"
    EDUCATION = "EDUCATION"
    GOVERNMENT = "GOVERNMENT"
    CHARITY = "CHARITY"
    INCOME = "INCOME"
    CASH = "CASH"


# Arabic display labels (what the dashboard shows).
LABELS_AR: dict[Category, str] = {
    Category.RESTAURANT: "مطاعم",
    Category.FOOD_DELIVERY: "توصيل طعام",
    Category.SHOPPING: "تسوّق",
    Category.GROCERY: "بقالة",
    Category.TELECOM: "اتصالات",
    Category.TRANSFER: "تحويلات",
    Category.OTHER: "أخرى",
    Category.FOOD: "مطاعم وطعام",
    Category.GROCERIES: "بقالة وتموين",
    Category.TRANSPORT: "نقل ووقود",
    Category.BILLS: "فواتير ومرافق",
    Category.HEALTH: "صحة وصيدليات",
    Category.ENTERTAINMENT: "ترفيه واشتراكات",
    Category.TRAVEL: "سفر وطيران",
    Category.EDUCATION: "تعليم",
    Category.GOVERNMENT: "خدمات حكومية",
    Category.CHARITY: "صدقات وتبرعات",
    Category.INCOME: "دخل ورواتب",
    Category.CASH: "سحب نقدي",
}

# English labels (secondary; useful for LTR views / logs).
LABELS_EN: dict[Category, str] = {
    Category.RESTAURANT: "Restaurants",
    Category.FOOD_DELIVERY: "Food Delivery",
    Category.SHOPPING: "Shopping",
    Category.GROCERY: "Groceries",
    Category.TELECOM: "Telecom",
    Category.TRANSFER: "Transfers",
    Category.OTHER: "Other",
    Category.FOOD: "Food & Dining",
    Category.GROCERIES: "Groceries",
    Category.TRANSPORT: "Transport & Fuel",
    Category.BILLS: "Bills & Utilities",
    Category.HEALTH: "Health & Pharmacy",
    Category.ENTERTAINMENT: "Entertainment",
    Category.TRAVEL: "Travel",
    Category.EDUCATION: "Education",
    Category.GOVERNMENT: "Government",
    Category.CHARITY: "Charity",
    Category.INCOME: "Income",
    Category.CASH: "Cash",
}


# Chart colors per category (reuses the dashboard palette).
COLORS: dict[Category, str] = {
    Category.RESTAURANT: "#e07a45",
    Category.FOOD_DELIVERY: "#eb9366",
    Category.SHOPPING: "#8b7ec8",
    Category.GROCERY: "#2f8f74",
    Category.TELECOM: "#3a4a7a",
    Category.TRANSFER: "#6d5fb0",
    Category.OTHER: "#c7ccd8",
    Category.FOOD: "#e07a45",
    Category.GROCERIES: "#2f8f74",
    Category.TRANSPORT: "#3f7fbf",
    Category.BILLS: "#d9a441",
    Category.HEALTH: "#4bb37b",
    Category.ENTERTAINMENT: "#c85c8e",
    Category.TRAVEL: "#2fa3a3",
    Category.EDUCATION: "#6d8b3a",
    Category.GOVERNMENT: "#5b6b8c",
    Category.CHARITY: "#c0562f",
    Category.INCOME: "#1aa06b",
    Category.CASH: "#8a8f98",
}


# Khawarizm lowercase category key (from the generated CSVs) -> Midd enum.
KHAWARIZM_KEY_MAP: dict[str, Category] = {
    "food": Category.FOOD,
    "groceries": Category.GROCERIES,
    "transport": Category.TRANSPORT,
    "shopping": Category.SHOPPING,
    "bills": Category.BILLS,
    "telecom": Category.TELECOM,
    "health": Category.HEALTH,
    "entertainment": Category.ENTERTAINMENT,
    "travel": Category.TRAVEL,
    "education": Category.EDUCATION,
    "government": Category.GOVERNMENT,
    "charity": Category.CHARITY,
    "transfer": Category.TRANSFER,
    "income": Category.INCOME,
    "cash": Category.CASH,
}


def from_khawarizm(key: str) -> Category:
    """Map a generated-dataset category key to the enum; unknown/blank -> OTHER."""
    return KHAWARIZM_KEY_MAP.get((key or "").strip().lower(), Category.OTHER)


def label_ar(category: Category) -> str:
    return LABELS_AR[category]


def color(category: Category) -> str:
    return COLORS[category]


def label_en(category: Category) -> str:
    return LABELS_EN[category]
