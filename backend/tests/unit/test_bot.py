"""Tests for bot brain, tools, emotion, and persistence."""

import pytest


class TestBotBrain:
    """Test Bot Brain components."""

    def test_personas_exist(self):
        from app.services.bot.brain import BOT_PERSONAS
        assert "clawford" in BOT_PERSONAS
        assert "nexus" in BOT_PERSONAS
        assert "buddy" in BOT_PERSONAS

    def test_persona_has_required_fields(self):
        from app.services.bot.brain import BOT_PERSONAS
        for pid, persona in BOT_PERSONAS.items():
            assert "name" in persona, f"{pid} missing name"
            assert "personality" in persona, f"{pid} missing personality"
            assert "greeting" in persona, f"{pid} missing greeting"
            assert "role" in persona, f"{pid} missing role"
            assert "expertise" in persona, f"{pid} missing expertise"

    def test_get_persona_default(self):
        from app.services.bot.brain import get_persona
        p = get_persona()
        assert p["name"] == "Clawford"

    def test_set_and_get_persona(self):
        from app.services.bot.brain import get_persona, set_persona
        set_persona("nexus", "test_user_999")
        p = get_persona("test_user_999")
        assert p["name"] == "Nexus"
        # Reset
        set_persona("clawford", "test_user_999")

    def test_system_prompt_contains_persona(self):
        from app.services.bot.brain import build_system_prompt, BOT_PERSONAS
        prompt = build_system_prompt(BOT_PERSONAS["clawford"])
        assert "Clawford" in prompt
        assert "Financial analysis" in prompt

    def test_max_iterations_constant(self):
        from app.services.bot.brain import MAX_TOOL_ITERATIONS
        assert MAX_TOOL_ITERATIONS == 5


class TestBotTools:
    """Test tool registration and definitions."""

    def test_tools_registered(self):
        from app.services.bot.tools import get_tool_definitions
        tools = get_tool_definitions("user")
        assert len(tools) > 0

    def test_admin_tools_more_than_user(self):
        from app.services.bot.tools import get_tool_definitions
        user_tools = get_tool_definitions("user")
        admin_tools = get_tool_definitions("admin")
        assert len(admin_tools) >= len(user_tools)

    def test_tool_has_function_schema(self):
        from app.services.bot.tools import get_tool_definitions
        tools = get_tool_definitions("admin")
        for tool in tools:
            assert "function" in tool, f"Tool missing function key"
            assert "name" in tool["function"]
            assert "description" in tool["function"]


class TestBotEmotion:
    """Test emotion mapping."""

    def test_emotion_for_event(self):
        from app.services.bot.emotion import get_emotion
        result = get_emotion("tool_success", {})
        assert "emotion" in result

    def test_emotion_for_content(self):
        from app.services.bot.emotion import get_emotion_for_content
        result = get_emotion_for_content("Everything looks great!")
        assert "emotion" in result

    def test_emotion_for_error_content(self):
        from app.services.bot.emotion import get_emotion_for_content
        result = get_emotion_for_content("Error: something failed")
        assert "emotion" in result


class TestBotModels:
    """Test bot database models."""

    def test_bot_message_model(self):
        from app.models.bot import BotMessage
        cols = {c.key for c in BotMessage.__table__.columns}
        for field in ["user_id", "direction", "msg_type", "content", "emotion", "tool_calls"]:
            assert field in cols

    def test_bot_scene_model(self):
        from app.models.bot import BotScene
        cols = {c.key for c in BotScene.__table__.columns}
        for field in ["scene_key", "priority", "emotion", "action", "template", "is_active"]:
            assert field in cols

    def test_bot_preference_model(self):
        from app.models.bot import BotPreference
        cols = {c.key for c in BotPreference.__table__.columns}
        for field in ["user_id", "mode", "persona_id", "position_x", "position_y", "bot_size", "bot_enabled"]:
            assert field in cols


class TestBotPersistence:
    """Test persistence constants."""

    def test_retention_days(self):
        from app.services.bot.persistence import RETENTION_DAYS
        assert RETENTION_DAYS == 30

    def test_context_window(self):
        from app.services.bot.persistence import BOT_CONTEXT_WINDOW
        assert BOT_CONTEXT_WINDOW == 5
