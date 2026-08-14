import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DefaultAssistantUiBoundaryTest(unittest.TestCase):
    def test_kmrag_agent_does_not_render_an_intro_panel(self):
        chat_source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")
        entry_source = (ROOT / "frontend" / "assets" / "modules" / "entry.js").read_text(encoding="utf-8")
        workflow_source = (ROOT / "frontend" / "assets" / "modules" / "workflow.js").read_text(encoding="utf-8")

        self.assertIn("state.currentAgentId === KMRAG_AGENT_ID", chat_source)
        self.assertNotIn("showKmragKnowledgeIntro", chat_source)
        self.assertNotIn("showKmragKnowledgeIntro", entry_source)
        self.assertNotIn("showKmragKnowledgeIntro", workflow_source)
        self.assertIn(
            "dom.workflowDock.style.display = state.currentAgentId === KMRAG_AGENT_ID ? 'none' : '';",
            chat_source,
        )

    def test_default_intro_only_renders_for_default_agent(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertIn("state.currentAgentId === 'default' && _showDefaultAssistantIntro", source)
        self.assertNotIn("if (_showDefaultAssistantIntro) {\n    _showDefaultAssistantIntro();", source)

    def test_default_intro_survives_agent_reload_with_existing_chat_log(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertIn("const shouldShowDefaultIntro = state.currentAgentId === 'default' && _showDefaultAssistantIntro;", source)
        self.assertIn("if (shouldShowDefaultIntro) {\n      _showDefaultAssistantIntro();", source)
        self.assertNotIn("if (!restoredLog && state.currentAgentId === 'default' && _showDefaultAssistantIntro)", source)

    def test_agent_switch_preserves_page_session_id(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertNotIn("resetSession", source)

    def test_agent_switch_saves_and_restores_log_by_agent(self):
        shared_source = (ROOT / "frontend" / "assets" / "modules" / "shared.js").read_text(encoding="utf-8")
        chat_source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertIn("agentLogSnapshots: {}", shared_source)
        self.assertIn("function saveCurrentAgentLog()", chat_source)
        self.assertIn("function restoreAgentLog(agentId)", chat_source)
        self.assertIn("saveCurrentAgentLog();", chat_source)
        self.assertIn("restoreAgentLog(state.currentAgentId)", chat_source)
        self.assertIn("const agentChanged = selectedAgentId !== previousAgentId;", chat_source)
        self.assertNotIn("if (hadProcessWorkflow || dom.log.querySelector('.process-workflow-msg'))", chat_source)
        self.assertNotIn("clearLog();", chat_source)

    def test_agent_names_use_loaded_agent_map_instead_of_selected_option_first(self):
        shared_source = (ROOT / "frontend" / "assets" / "modules" / "shared.js").read_text(encoding="utf-8")
        chat_source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertIn("agentNamesById: {}", shared_source)
        self.assertIn("state.agentNamesById[agent.id || 'default'] = agent.name || agent.id || 'default';", chat_source)
        self.assertIn("const mappedName = state.agentNamesById[state.currentAgentId];", chat_source)
        self.assertIn("if (mappedName) return mappedName;", chat_source)

    def test_agent_switch_does_not_add_chat_notice(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "chat.js").read_text(encoding="utf-8")

        self.assertNotIn("已切换智能体", source)
        self.assertNotIn("addBotMsg('已切换智能体", source)
        self.assertNotIn("if (_showProcessAutoWorkflow) _showProcessAutoWorkflow();\n    return;", source)

    def test_default_intro_does_not_expose_process_auto_internal_id(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "workflow.js").read_text(encoding="utf-8")

        self.assertIn("请切换到工艺自动生成智能体", source)
        self.assertNotIn("process-auto-generate-agent 智能体", source)


    def test_process_workflow_run_all_button_uses_dynamic_contiguous_progress(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "workflow.js").read_text(encoding="utf-8")

        self.assertIn("function getProcessWorkflowAutoStartIndex()", source)
        self.assertIn("function getProcessWorkflowRunAllLabel()", source)
        self.assertIn("function clearProcessWorkflowDoneStepsFromIndex(startIndex)", source)
        self.assertIn("getProcessWorkflowRunAllLabel()", source)
        self.assertIn("const startIndex = getProcessWorkflowAutoStartIndex();", source)
        self.assertIn("for (let i = startIndex; i < PROCESS_AUTO_WORKFLOW_STEPS.length; i += 1)", source)
        self.assertNotIn("continueFromStepId ? '继续执行2-5步' : '一键执行1-5步'", source)

    def test_ai_process_input_retry_window_allows_slow_inference(self):
        process_route_source = (ROOT / "frontend" / "assets" / "modules" / "process_route.js").read_text(encoding="utf-8")
        workflow_source = (ROOT / "frontend" / "assets" / "modules" / "workflow.js").read_text(encoding="utf-8")

        self.assertIn("maxRetries: 30", process_route_source)
        self.assertIn("retryDelayMs: 3000", process_route_source)
        self.assertIn("waitForProcessWorkflowStepDone(stepId, 900000)", workflow_source)
        self.assertIn("已重试 ' + PROCESS_RETRY_CONFIG.maxRetries + ' 次", process_route_source)

    def test_ai_process_input_json_receipt_forces_route_panel_open(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "process_route.js").read_text(encoding="utf-8")

        self.assertIn("export function unlockProcessRoutePanelForInput(payload)", source)
        self.assertIn("openProcessRoutePanel(true);", source)

    def test_process_route_submit_surfaces_top_level_api_errors(self):
        source = (ROOT / "frontend" / "assets" / "modules" / "process_route.js").read_text(encoding="utf-8")

        self.assertIn("if (data && data.status === 'error')", source)
        self.assertIn("data.message || data.error_code || 'submit process route failed'", source)


if __name__ == "__main__":
    unittest.main()
