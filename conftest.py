import pytest

@pytest.fixture
def get_log_data(deploy_client, contracts):
    def _get_log_data(event, txn_hash):
        event_logs = event.get_transaction_logs(txn_hash)
        assert len(event_logs)

        if len(event_logs) == 1:
            event_data = event.get_log_data(event_logs[0])
        else:
            event_data = tuple(event.get_log_data(l) for l in event_logs)
        return event_data
    return _get_log_data
