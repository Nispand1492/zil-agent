import pytest
from unittest.mock import patch
from agent import run_agent

@patch("agent.update_profile.add_to_list_field")
@patch("agent.update_profile.remove_from_list_field")
@patch("agent.update_profile.set_string_field")
def test_add_and_remove_pending_question(mock_set_string, mock_remove, mock_add):
    user_id = "testuser@example.com"

    # --- Step 1: Agent encounters missing info and adds a pending question ---
    prompt1 = "I don't remember the exact dates of my internship."
    mock_add.return_value = "OK"
    
    response1 = run_agent(prompt1, user_id)

    # Expect it to have queued the follow-up question
    mock_add.assert_called_with(user_id, field_name="pending_questions", item=pytest.any(str)) # type: ignore
    assert "ask" in response1.lower() or "later" in response1.lower()

    # Simulate that the agent asked: "When did your internship take place?"
    pending_question = "When did your internship take place?"

    # --- Step 2: User answers it, agent removes it from pending ---
    mock_set_string.return_value = "OK"
    mock_remove.return_value = "OK"

    prompt2 = "It was during summer 2021 at Infosys."
    response2 = run_agent(prompt2, user_id)

    # Expect it to call SetStringField for date or experience_paragraphs
    assert mock_set_string.called

    # Expect it to remove the question
    mock_remove.assert_any_call(user_id, field_name="pending_questions", item=pending_question)
    assert "thank" in response2.lower() or "updated" in response2.lower()
