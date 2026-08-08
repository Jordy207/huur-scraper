from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from src.config import Settings
from src.filtering.rules import evaluate_listing
from src.notify.formatter import format_listing_message
from src.notify.telegram import TelegramNotifier
from src.policy.risk_policy import SourcePolicy, is_collection_allowed
from src.scrapers.base import SourceBlockedError
from src.scrapers.registry import load_source_policies
from src.scrapers.source_health import SourceHealthState, SourceHealthTracker
from src.storage.sqlite_store import SQLiteStore


logger = logging.getLogger(__name__)


def run_all_sources(
    settings: Settings,
    store: SQLiteStore,
    source_factories: dict[str, callable],
    registry_file: Path,
    selected_sources: set[str] | None = None,
) -> None:
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    health_tracker = SourceHealthTracker()
    policies = load_source_policies(registry_file)
    logger.info("Loaded %d source policies from %s", len(policies), registry_file)
    logger.info("Telegram enabled: %s", notifier.enabled)

    for policy in policies:
        logger.info("Evaluating source=%s mode=%s", policy.name, policy.mode.value)
        if selected_sources and policy.name not in selected_sources:
            logger.info("Skipping source=%s because it is not selected", policy.name)
            continue

        if not is_collection_allowed(policy):
            logger.info("Skipping source=%s due to policy mode=%s", policy.name, policy.mode.value)
            store.write_source_run(
                source_site=policy.name,
                run_at=datetime.utcnow().isoformat(),
                status="skipped",
                details=f"mode={policy.mode.value}",
            )
            continue

        factory = source_factories.get(policy.name)
        if factory is None:
            logger.warning("No adapter for source=%s", policy.name)
            store.write_source_run(
                source_site=policy.name,
                run_at=datetime.utcnow().isoformat(),
                status="error",
                details="no scraper adapter",
            )
            continue

        scraper = factory(settings)
        try:
            logger.info("Running source=%s", policy.name)
            listings = scraper.search(max_retries=policy.max_retries)
            health_tracker.mark_success(policy.name)
            logger.info("Source=%s returned %d listings", policy.name, len(listings))

            changed_count = 0
            alerted_count = 0

            for listing in listings:
                upsert = store.upsert_listing(listing)
                if not upsert.changed:
                    continue
                changed_count += 1

                match = evaluate_listing(listing, settings)
                if not (match.is_hard_match or match.is_close_match):
                    continue

                message = format_listing_message(listing, match)
                notifier.send_message(message)
                alerted_count += 1

            logger.info(
                "Source=%s changed=%d alerted=%d",
                policy.name,
                changed_count,
                alerted_count,
            )

            store.write_source_run(
                source_site=policy.name,
                run_at=datetime.utcnow().isoformat(),
                status="ok",
                details=f"listings={len(listings)},changed={changed_count},alerted={alerted_count}",
            )

        except SourceBlockedError as error:
            logger.warning("Source blocked source=%s error=%s", policy.name, error)
            state = health_tracker.mark_block(policy.name)
            details = f"blocked: {error}"
            if policy.auto_disable_on_block and state == SourceHealthState.BLOCKED:
                details = f"{details}; action=disable-suggested"

            store.write_source_run(
                source_site=policy.name,
                run_at=datetime.utcnow().isoformat(),
                status="blocked",
                details=details,
            )

            if notifier.enabled:
                notifier.send_message(f"[SOURCE_BLOCKED] {policy.name} - {state.value}")

        except Exception as error:  # noqa: BLE001
            logger.exception("Source failed source=%s", policy.name)
            store.write_source_run(
                source_site=policy.name,
                run_at=datetime.utcnow().isoformat(),
                status="error",
                details=str(error),
            )
            if notifier.enabled:
                notifier.send_message(f"[SOURCE_ERROR] {policy.name} - {error}")
