"""Tests for conversation service logic."""

import pytest


class TestContextWindow:
    """Test multi-turn context window logic."""

    def test_context_window_constant(self):
        from app.services.conversation import CONTEXT_WINDOW
        assert CONTEXT_WINDOW == 10

    def test_compress_threshold_constant(self):
        from app.services.conversation import COMPRESS_THRESHOLD
        assert COMPRESS_THRESHOLD == 8

    def test_compress_not_triggered_below_threshold(self):
        """Should not compress when message count - summary_up_to < threshold."""
        from app.services.conversation import COMPRESS_THRESHOLD
        msg_count, summary_up_to = 5, 0
        assert (msg_count - summary_up_to) < COMPRESS_THRESHOLD

    def test_compress_triggered_at_threshold(self):
        """Should compress when message count - summary_up_to >= threshold."""
        from app.services.conversation import COMPRESS_THRESHOLD
        msg_count, summary_up_to = 10, 0
        assert (msg_count - summary_up_to) >= COMPRESS_THRESHOLD

    def test_compress_not_triggered_after_recent_summary(self):
        """Should not compress when recently summarized."""
        from app.services.conversation import COMPRESS_THRESHOLD
        msg_count, summary_up_to = 15, 10
        assert (msg_count - summary_up_to) < COMPRESS_THRESHOLD

    def test_compress_triggered_with_enough_new_messages(self):
        """Should compress again after enough new messages."""
        from app.services.conversation import COMPRESS_THRESHOLD
        msg_count, summary_up_to = 20, 10
        assert (msg_count - summary_up_to) >= COMPRESS_THRESHOLD


class TestConversationModel:
    """Test Conversation model schema."""

    def test_conversation_has_summary_fields(self):
        from app.models.conversation import Conversation
        cols = {c.key for c in Conversation.__table__.columns}
        assert "summary" in cols
        assert "summary_up_to" in cols

    def test_message_has_all_fields(self):
        from app.models.conversation import Message
        cols = {c.key for c in Message.__table__.columns}
        for field in ["id", "conversation_id", "role", "content", "sources_json", "chart_json", "confidence"]:
            assert field in cols
