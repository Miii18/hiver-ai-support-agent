from __future__ import annotations

from typing import Iterable


class PromptBuilder:
    """Builds a grounded support prompt from retrieved context and the current conversation."""

    def build_prompt(
        self,
        query: str,
        context: Iterable[dict],
        intent_label: str,
        memory_context: str | None = None,
    ) -> str:
        context_entries = list(context)
        context_text = ''
        if context_entries:
            for idx, item in enumerate(context_entries, start=1):
                customer = str(item.get('customer_query') or item.get('conversation', '')).strip()
                amazon = str(item.get('amazon_response') or item.get('response', '')).strip()
                similarity = item.get('similarity_score')
                context_text += (
                    f"\n[{idx}] Intent: {item.get('intent_label', intent_label)} | "
                    f"Similarity: {similarity}\nCustomer: {customer[:400]}\nAmazon: {amazon[:400]}\n"
                )
        else:
            context_text = '\nNo relevant retrieved context found.'

        memory_block = memory_context if memory_context else 'No previous conversation context available.'
        return (
            'You are a helpful Amazon support assistant. Answer using only the retrieved support context and the current query.\n'
            'Do not invent order data, account details, or internal policies.\n\n'
            f'User query: {query}\n'
            f'Detected intent: {intent_label}\n'
            f'Prior conversation context: {memory_block}\n\n'
            'Grounded context from similar customer conversations:\n'
            f'{context_text}\n\n'
            'Instructions: provide a concise, empathetic answer grounded in the evidence above and include next-best steps where relevant.'
        )
