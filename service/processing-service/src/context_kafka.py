from __future__ import annotations

from processing_service.context import (
    ContextTransition,
)


DEFAULT_CONTEXT_TOPIC = (
    "ims.context.transition"
)


def build_context_key(
    transition: ContextTransition,
) -> bytes:
    """
    Preserva afinidade de partição para
    todas as transições da mesma dimensão
    contextual e do mesmo escopo.
    """

    value = (
        f"{transition.scope_type.value}:"
        f"{transition.scope_id}:"
        f"{transition.context_logical_name}"
    )

    return value.encode(
        "utf-8"
    )
