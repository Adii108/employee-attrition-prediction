# Helper utilities for formatting and small helper tasks

def format_percentage(val: float) -> str:
    """Formats a float probability value into a percentage string."""
    return f"{val * 100:.2f}%"
