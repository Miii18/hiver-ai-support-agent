from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

from src.chatbot.memory import ConversationMemory
from src.chatbot.prompt_builder import PromptBuilder
from src.chatbot.query_classifier import QueryClassifier
from src.chatbot.response_formatter import ResponseFormatter
from src.chatbot.chatbot import SupportChatbot

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_memory_tracks_turns() -> None:
    memory = ConversationMemory(max_turns=3)
    memory.add_turn('user', 'where is my order?')
    memory.add_turn('assistant', 'I can help check the delivery status.')
    history = memory.get_recent_context()
    assert len(history) == 2
    assert history[0]['role'] == 'user'
    assert history[1]['role'] == 'assistant'


def test_prompt_builder_includes_context() -> None:
    builder = PromptBuilder()
    prompt = builder.build_prompt(
        query='where is my order?',
        context=[{'customer_query': 'Where is my package?', 'amazon_response': 'Please check the order tracking link.'}],
        intent_label='Customer Amazon Order',
        memory_context='Previous answer: order status.',
    )
    assert 'where is my order?' in prompt
    assert 'Customer Amazon Order' in prompt
    assert 'Previous answer: order status.' in prompt


def test_query_classifier_returns_intent() -> None:
    classifier = QueryClassifier()
    result = classifier.classify('where is my order?')
    assert result['intent_label']
    assert result['intent_category']
    assert 0.0 <= float(result['confidence']) <= 1.0


def test_response_formatter_schema() -> None:
    payload = ResponseFormatter.format_response(
        answer='Your package may be delayed.',
        intent_label='Customer Amazon Order',
        intent_category='Orders',
        confidence=0.82,
        context=[{'conversation_id': 'c1', 'similarity_score': 0.91}],
    )
    assert payload['answer']
    assert payload['intent_label'] == 'Customer Amazon Order'
    assert payload['intent_category'] == 'Orders'
    assert payload['confidence'] == 0.82
    assert payload['context'][0]['conversation_id'] == 'c1'


def test_support_chatbot_answers_query() -> None:
    chatbot = SupportChatbot(top_k=3)
    response = chatbot.answer_query('where is my order?')
    assert 'answer' in response
    assert response['intent_label']
    assert isinstance(response['context'], list)
    assert len(response['context']) <= 3


def test_phase7_success_banner_exact(capsys, monkeypatch) -> None:
    root = PROJECT_ROOT
    spec = importlib.util.spec_from_file_location('phase7_runner', root / 'scripts' / 'run_phase7.py')
    runner = importlib.util.module_from_spec(spec)
    assert spec and spec.loader is not None
    spec.loader.exec_module(runner)

    monkeypatch.setattr(runner, 'SupportChatbot', lambda *args, **kwargs: type('DummyBot', (), {
        'answer_query': lambda self, query: {
            'answer': 'test answer',
            'intent_label': 'Customer Amazon Order',
            'intent_category': 'Orders',
            'confidence': 0.9,
            'context': [{'conversation_id': 'c1', 'similarity_score': 0.88}],
            'memory_summary': {'turn_count': 1},
        }
    })())
    exit_code = runner.run()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert '# ====================================================== PHASE 7 COMPLETED SUCCESSFULLY' in captured.out


if __name__ == '__main__':
    test_memory_tracks_turns()
    test_prompt_builder_includes_context()
    test_query_classifier_returns_intent()
    test_response_formatter_schema()
    test_support_chatbot_answers_query()
    test_phase7_success_banner_exact()
