deploy_contracts = [
    "Target",
    "ReplicatorFactory",
]


def test_factory(deployed_contracts, deploy_client, get_log_data, denoms):
    rf = deployed_contracts.ReplicatorFactory
    target = deployed_contracts.Target

    target_block = deploy_client.get_block_number() + 200

    txn_h, txn_r = rf.build.s('test', 0, target_block, target._meta.address, value=1000 * denoms.ether)

    log_data = get_log_data(rf.Replicated, txn_h)

    assert log_data
    addr = log_data['replicator']

    assert len(deploy_client.get_code(addr)) > 2


def test_replication(deployed_contracts, deploy_client, get_log_data, denoms, contracts):
    rf = deployed_contracts.ReplicatorFactory
    target = deployed_contracts.Target

    target_block = deploy_client.get_block_number() + 200

    txn_h, txn_r = rf.build.s('test', 0, target_block, target._meta.address, value=1000 * denoms.ether)

    log_data = get_log_data(rf.Replicated, txn_h)

    replicator = contracts.Replicator(log_data['replicator'], deploy_client)
    txn_h, txn_r = replicator.replicate.s()

    log_data = get_log_data(rf.Replicated, txn_h)
    replicator = contracts.Replicator(log_data['replicator'], deploy_client)

    assert replicator.targetBlock() == target_block
    assert replicator.target() == target._meta.address
    assert replicator.generation() == 1


def test_it(deployed_contracts, deploy_client, get_log_data, contracts, denoms):
    rf = deployed_contracts.ReplicatorFactory
    target = deployed_contracts.Target

    target_block = deploy_client.get_block_number() + 25

    txn_h, txn_r = rf.build.s('test', 0, target_block, target._meta.address, value=1000 * denoms.ether)

    replicators = []

    log_data = get_log_data(rf.Replicated, txn_h)
    assert log_data
    addr = log_data['replicator']

    replicators.append(addr)

    while deploy_client.get_block_number() < target_block:
        txn_data = [contracts.Replicator(addr, deploy_client).replicate.s() for addr in replicators]
        for txn_h, txn_r in txn_data:
            log_data = get_log_data(rf.Replicated, txn_h)
            assert log_data
            addr = log_data['replicator']

            replicators.append(addr)

    assert target.totalHits() == 0

    for addr in replicators:
        replicator = contracts.Replicator(addr, deploy_client)
        replicator.execute.s()

    assert target.totalHits() == len(replicators) == 32
