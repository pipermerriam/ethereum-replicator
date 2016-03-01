def get_log_data(event, txn_hash):
    event_logs = event.get_transaction_logs(txn_hash)
    assert len(event_logs)

    if len(event_logs) == 1:
        event_data = event.get_log_data(event_logs[0])
    else:
        event_data = tuple(event.get_log_data(l) for l in event_logs)
    return event_data


def find_all_replecators(factory, start_block, end_block, blockchain_client):
    replecators = []
    for block_number in range(start_block, end_block + 1):
        block = blockchain_client.get_block_by_number(block_number, False)
        for txn_h in block['transactions']:
            try:
                event_data = get_log_data(factory.Replicated, txn_h)
            except AssertionError:
                continue
            if isinstance(event_data, dict):
                replecators.append(event_data)
            else:
                replecators.extend(event_data)

    return replecators

ether = 1000000000000000000.0

def cleanup_replicators(replicators, Replicator, blockchain_client):
    txns = []
    for replicator in replicators:
        addr = replicator['replicator']
        if blockchain_client.get_balance(addr) == 0:
            print "{0}: no ether".format(addr)
            continue
        if len(blockchain_client.get_code(addr)) < 5:
            print "{0}: no code".format(addr)
            continue
        rp = Replicator(addr, blockchain_client)
        if rp.targetBlock() > blockchain_client.get_block_number():
            print "{0}: too soon".format(addr)
            continue
        balance = blockchain_client.get_balance(addr)
        print "{0}: recovering {1}".format(addr, balance / ether)
        txn_h = rp.execute()
        txns.append(txn_h)
    return txns

