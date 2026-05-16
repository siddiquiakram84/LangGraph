from typing import TypedDict, Optional, Any, List, Dict


class HealingState(TypedDict, total=False):

    driver: Any

    failed_locator: tuple[str, str]

    failed_action: str

    error_message: str

    stack_trace: str

    test_file: str

    dom_snapshot: str

    screenshot_path: str

    candidate_locators: List[tuple[str, str]]

    healed_locator: Optional[tuple[str, str]]

    confidence_score: float

    memory_results: Optional[Dict]

    validation_success: bool

    logic_suggestion: Optional[str]

    success: bool

    report: Dict[str, Any]
