"""LLM-based reranker using OpenAI API for confidence scoring"""

import asyncio

import numpy as np
import structlog
from openai import AsyncOpenAI

from api.models import EventResult
from shared.config import settings

logger = structlog.get_logger()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Token IDs for "True" and "False" tokens in gpt-4.1-nano
# See: https://tiktokenizer.vercel.app/?model=o200k_base
TRUE_TOKEN_ID = 4710
FALSE_TOKEN_ID = 8168


async def rerank_results(
    query: str,
    results: list[EventResult],
    min_score: float = 0.5,
) -> list[EventResult]:
    """
    Rerank results using LLM confidence scoring.

    Uses OpenAI's API to evaluate relevance of each result to the query,
    returning only high-confidence matches. This implements the single-token
    evaluation technique for efficient LLM-based reranking.

    Args:
        query: The original search query
        results: List of search results to rerank
        min_score: Minimum confidence score to include (0.0-1.0)

    Returns:
        Filtered and reranked results based on LLM confidence scores.
        May return fewer than input if results score below threshold.
    """
    if not results:
        return []

    # Create concurrent evaluation tasks
    tasks = []
    for result in results:
        task = openai_client.chat.completions.create(
            model="gpt-4.1-nano",  # Supports logprobs
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at determining whether a "
                        "prediction market event is relevant to a search query."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f'Respond with "True" if the EVENT is relevant to the '
                        f'QUERY and "False" otherwise.\n\n'
                        f"<EVENT>\n{result.search_text}\n</EVENT>\n\n"
                        f"<QUERY>\n{query}\n</QUERY>"
                    ),
                },
            ],
            temperature=0,
            max_completion_tokens=1,
            logit_bias={
                str(TRUE_TOKEN_ID): 1,
                str(FALSE_TOKEN_ID): 1,
            },  # Bias toward True/False
            logprobs=True,
            top_logprobs=2,
        )
        tasks.append(task)

    # Execute all reranking requests concurrently
    try:
        responses = await asyncio.gather(*tasks)
    except Exception as e:
        logger.error("Failed to rerank results", error=str(e))
        # On error, return original results without reranking
        return results

    # Process scores
    scored_results = []
    for result, response in zip(results, responses, strict=True):
        try:
            logprobs = response.choices[0].logprobs
            if not logprobs or not logprobs.content:
                # No logprobs, skip this result
                continue

            top_logprobs = logprobs.content[0].top_logprobs
            if not top_logprobs:
                continue

            # Get the probability of the top token
            token = top_logprobs[0].token
            log_prob = top_logprobs[0].logprob
            prob = np.exp(log_prob)

            # Calculate relevance score
            # If token is "True" (or truthy), use prob directly
            # If token is "False" (or falsy), use 1 - prob
            score = prob if token.lower() == "true" else (1 - prob)

            # Only include results above threshold
            if score >= min_score:
                # Update the rank to reflect confidence score
                result.rank = float(score)
                scored_results.append(result)

        except Exception as e:
            logger.warning(
                "Failed to score result, skipping",
                error=str(e),
                result=result.platform_id,
            )
            continue

    # Sort by score (descending - higher confidence first)
    scored_results.sort(key=lambda x: x.rank, reverse=True)

    logger.info(
        "Reranking completed",
        original_count=len(results),
        filtered_count=len(scored_results),
        min_score=min_score,
    )

    return scored_results
