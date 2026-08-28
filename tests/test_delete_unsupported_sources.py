from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ceatw_update_pipeline.scripts.delete_unsupported_sources import (
    delete_unsupported_sources,
    get_allowed_country_codes,
    run,
)


def test_get_allowed_country_codes():
    codes = get_allowed_country_codes()
    assert isinstance(codes, set)
    assert "US" in codes
    assert "DE" in codes
    assert "GB-ENG" in codes
    assert "GB-SCT" in codes
    assert "GB-WLS" in codes
    assert "GB-NIR" in codes
    assert "AQ" not in codes  # Antarctica should not be in Datawrapper codes
    assert "AI" not in codes  # Anguilla should not be in Datawrapper codes


@pytest.mark.anyio
async def test_delete_unsupported_sources_no_records():
    mock_session = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.all.return_value = []
    mock_session.execute.return_value = mock_execute_result

    deleted_count = await delete_unsupported_sources(mock_session)
    assert deleted_count == 0
    assert mock_session.execute.call_count == 1


@pytest.mark.anyio
async def test_delete_unsupported_sources_with_records():
    mock_session = AsyncMock()

    # 1. Summary query returns unsupported countries
    mock_summary_result = MagicMock()
    mock_summary_result.all.return_value = [("AI", 3), ("AQ", 1)]

    # 2. Highlight delete result
    mock_highlight_result = MagicMock()
    mock_highlight_result.rowcount = 4

    # 3. Source delete result
    mock_source_result = MagicMock()
    mock_source_result.rowcount = 4

    mock_session.execute.side_effect = [
        mock_summary_result,
        mock_highlight_result,
        mock_source_result,
    ]

    deleted_count = await delete_unsupported_sources(mock_session)
    assert deleted_count == 4
    assert mock_session.execute.call_count == 3


@pytest.mark.anyio
@patch("ceatw_update_pipeline.scripts.delete_unsupported_sources.kill_engine", new_callable=AsyncMock)
@patch("ceatw_update_pipeline.scripts.delete_unsupported_sources.get_session")
@patch("ceatw_update_pipeline.scripts.delete_unsupported_sources.delete_unsupported_sources", new_callable=AsyncMock)
async def test_run_script(mock_delete, mock_get_session, mock_kill_engine):
    mock_session_ctx = MagicMock()
    mock_session = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
    mock_get_session.return_value = mock_session_ctx

    mock_delete.return_value = 5

    await run()

    mock_delete.assert_called_once_with(mock_session)
    mock_kill_engine.assert_called_once()

