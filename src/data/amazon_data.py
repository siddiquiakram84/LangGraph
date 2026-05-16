"""
Layer: Data
Responsibility: Test data management and parameterisation.
Tests never hardcode test data — they import from here.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AmazonSearchData:
    keyword: str
    expected_results_contain: str


AMAZON_SEARCH_CASES = [
    AmazonSearchData(keyword="iphone 15",      expected_results_contain="iPhone"),
    AmazonSearchData(keyword="laptop",          expected_results_contain="Laptop"),
    AmazonSearchData(keyword="wireless mouse",  expected_results_contain="Mouse"),
]

AMAZON_DEFAULT_SEARCH = AmazonSearchData(
    keyword="iphone 15",
    expected_results_contain="iPhone",
)
