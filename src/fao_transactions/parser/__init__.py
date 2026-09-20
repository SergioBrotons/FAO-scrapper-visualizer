"""Parser package for extracting real-estate transaction notices."""

from fao_transactions.parser.models import TransactionRecord
from fao_transactions.parser.pdf_parser import FaoPdfParser

__all__ = ["TransactionRecord", "FaoPdfParser"]
