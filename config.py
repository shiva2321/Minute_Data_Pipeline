"""
Configuration module for the Minute Data Pipeline
"""
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
import ast
import operator

# Load environment variables
load_dotenv()


def _safe_eval_arith(expr: str) -> Optional[int]:
    """Safely evaluate simple arithmetic expressions to an integer.
    Supports +, -, *, //, / (floats rounded), and parentheses with integer literals.
    Returns None if expression is invalid.
    """
    try:
        node = ast.parse(expr, mode="eval").body
    except Exception:
        return None

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.FloorDiv: operator.floordiv,
        ast.Div: operator.truediv,
    }

    def _eval(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            val = _eval(n.operand)
            if val is None:
                return None
            return +val if isinstance(n.op, ast.UAdd) else -val
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            left = _eval(n.left)
            right = _eval(n.right)
            if left is None or right is None:
                return None
            return ops[type(n.op)](left, right)
        if isinstance(n, ast.Expr):
            return _eval(n.value)
        if isinstance(n, ast.Tuple):  # disallow tuples
            return None
        # disallow names, calls, attributes, etc.
        return None

    val = _eval(node)
    if val is None:
        return None
    try:
        return int(round(val))
    except Exception:
        return None


def _parse_int_env(var_name: str, default: int) -> int:
    """Parse integer from environment with support for simple arithmetic expressions.
    Fallback to provided default on failure.
    """
    raw = os.getenv(var_name)
    if raw is None or raw.strip() == "":
        return default
    raw = raw.strip()
    try:
        return int(raw)
    except ValueError:
        val = _safe_eval_arith(raw)
        return val if val is not None else default


class Settings(BaseModel):
    """Application settings loaded from environment variables"""

    # EODHD API Settings
    eodhd_api_key: str = Field(default_factory=lambda: os.getenv('EODHD_API_KEY', ''))
    eodhd_base_url: str = Field(default_factory=lambda: os.getenv('EODHD_BASE_URL', 'https://eodhd.com/api'))

    # MongoDB Settings
    mongodb_uri: str = Field(default_factory=lambda: os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    mongodb_database: str = Field(default_factory=lambda: os.getenv('MONGODB_DATABASE', 'stock_data'))
    mongodb_collection: str = Field(default_factory=lambda: os.getenv('MONGODB_COLLECTION', 'company_profiles'))

    # Pipeline Settings
    data_fetch_interval_days: int = Field(default_factory=lambda: _parse_int_env('DATA_FETCH_INTERVAL_DAYS', 30))
    max_workers: int = Field(default_factory=lambda: _parse_int_env('MAX_WORKERS', 5))
    batch_size: int = Field(default_factory=lambda: _parse_int_env('BATCH_SIZE', 100))

    # History Backfill Settings
    history_chunk_days: int = Field(default_factory=lambda: _parse_int_env('HISTORY_CHUNK_DAYS', 30))  # Changed from 30 to 30 for better API efficiency
    max_history_years: int = Field(default_factory=lambda: _parse_int_env('MAX_HISTORY_YEARS', 25))

    # Rate limiting
    api_calls_per_minute: int = Field(default_factory=lambda: _parse_int_env('API_CALLS_PER_MINUTE', 80))
    api_calls_per_day: int = Field(default_factory=lambda: _parse_int_env('API_CALLS_PER_DAY', 95000))
    backoff_on_error: bool = Field(default_factory=lambda: bool(int(os.getenv('BACKOFF_ON_ERROR', '1'))))
    initial_retry_delay: int = Field(default_factory=lambda: _parse_int_env('INITIAL_RETRY_DELAY', 5))
    max_retry_delay: int = Field(default_factory=lambda: _parse_int_env('MAX_RETRY_DELAY', 300))
    store_backfill_metadata: bool = Field(default_factory=lambda: bool(int(os.getenv('STORE_BACKFILL_METADATA', '1'))))
    backfill_log_path: str = Field(default_factory=lambda: os.getenv('BACKFILL_LOG_PATH', 'logs/backfill.log'))

    class Config:
        case_sensitive = False


# Global settings instance
settings = Settings()
