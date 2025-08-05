import pytest
from unittest.mock import patch
from agent import run_agent

@patch("agent.get_user_profile")
@patch("agent.update_profile.set_string_field")
@patch("agent.update_profile.remove_from_list_field")
def test_pending_questions_preamble(mock_remove, mock_set, mock_get_profile):
    user_id = "testuser@example.com"

    # Simulate profile with pending questions
    mock_get_profile.return_value = {
        "pending_questions": [
            "What is your current location?",
            "What is your highest degree?"
        ]
    }

    # Let agent update string fields and remove questions
    mock_set.return_value = "OK"
    mock_remove.return_value = "OK"

    # User says something general
    prompt = "Please update my profile with my new job at Meta."

    response = run_agent(prompt, user_id)

    # Check if the preamble was included and agent replied accordingly
    assert "location" in response.lower() or "degree" in response.lower()
    assert "meta" in response.lower() or "updated" in response.lower()
