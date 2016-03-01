contract SchedulerInterface {
    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address);
}

contract FactoryType {
    event Replicated(address replicator, bytes32 group, uint generation, uint targetBlock);

    function build(bytes32 group, uint generation, uint targetBlock, address target) public;
}

contract Replicator {
    FactoryType public factory;
    bytes32 public group;
    uint public generation;
    uint public targetBlock;
    address public target;
    address constant scheduler = 0x26416b12610d26fd31d227456e9009270574038f;

    function Replicator(bytes32 _group, uint _generation, uint _targetBlock, address _target) {
        group = _group;
        generation = _generation;
        targetBlock = _targetBlock;
        target = _target;
        factory = FactoryType(msg.sender);

        schedule();
    }

    function replicate() public {
        factory.build.value(this.balance / 2)(
            group,
            generation + 1,
            targetBlock,
            target
        );
        schedule();
    }

    function schedule() internal {
        if (this.balance < 4 ether || block.number + 50 >= targetBlock) {
            SchedulerInterface(scheduler).scheduleCall.value(2 ether)(
                bytes4(sha3("execute()")),
                targetBlock,
                500000
            );
        } else {
            SchedulerInterface(scheduler).scheduleCall.value(2 ether)(
                bytes4(sha3("replicate()")),
                block.number + 10,
                2900000
            );
        }
    }

    function execute() public {
        if (block.number < targetBlock) throw;
        target.call();
        selfdestruct(address(factory));
    }
}

contract ReplicatorFactory is FactoryType {
    address public owner;

    function ReplicatorFactory() {
        owner = msg.sender;
    }

    function build(bytes32 group, uint generation, uint targetBlock, address target) public {
        var replicator = (new Replicator).value(msg.value)(group, generation, targetBlock, target);
        Replicated(address(replicator), group, generation, targetBlock);
    }

    function() {
        owner.send(this.balance);
    }
}


contract Target {
    uint public firstBlock;
    uint public lastBlock;
    uint public totalHits;
    mapping (uint => uint) hitCounter;

    function () {
        hitCounter[block.number] += 1;
        totalHits += 1;
        if (firstBlock == 0) firstBlock = block.number;
        lastBlock = block.number;
    }
}
