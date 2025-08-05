import pytest
from unittest.mock import patch, MagicMock
from agent import run_agent

# Set your deployment name if needed, or use env var
deployment_name = "gpt-4o"

@patch("agent.update_profile.add_to_list_field")
@patch("agent.update_profile.set_string_field")
def test_basic_profile_building(mock_set_string, mock_add_to_list):
    # Setup mocks
    mock_set_string.return_value = "OK"
    mock_add_to_list.return_value = "OK"

    prompt = "I currently work at PwC as a Senior Analyst and have experience in audit and tax automation."
    user_id = "testuser@example.com"

    response = run_agent(prompt, user_id)

    # Assertions for tool usage
    mock_set_string.assert_any_call(user_id, field_name="current_title", value="Senior Analyst")
    mock_set_string.assert_any_call(user_id, field_name="current_company", value="PwC")

    # Audit and tax automation should be added as skills or custom_profile_notes
    assert mock_add_to_list.called

    # Optional: check response content
    assert isinstance(response, str)
    assert "updated" in response.lower() or "added" in response.lower()  # agent reply

@patch("agent.update_profile.add_to_list_field")
def test_skills_addition(mock_add_to_list):
    mock_add_to_list.return_value = "OK"

    prompt = "Add budgeting, Tableau, and Excel to my skills."
    user_id = "testuser@example.com"

    response = run_agent(prompt, user_id)

    expected_skills = ["budgeting", "Tableau", "Excel"]
    for skill in expected_skills:
        mock_add_to_list.assert_any_call(user_id, field_name="skills", item=skill)

    assert "added" in response.lower()
