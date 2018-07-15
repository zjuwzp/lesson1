#一个区块的结构如下：
# {
#     "index":0,      #区块的索引
#     "timestamp":"",
#     "transactions":[
#         {
#             "sender":"",
#             "recipient":"",
#             "amount":5,
#         }
#     ],
#     "proof":"",     #工作量证明
#     "previous_hash":"",     #上一个区块的哈希值
# }
from time import time
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):             #每个类中都应该包含一个构造函数
        self.chain = []             #这个数组中每个元素就是一个块
        self.nodes = set()          #保存节点信息，set中没有重复元素
        self.current_transactions = []      #数组存储当前交易的信息

        # 创建创世块，proof随便写。这个区块不用计算，因为里面没有任何内容
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)       #parsed_url.netloc取得的地址形式是：ip：port

    def new_block(self, proof, previous_hash = None):            #添加块的方法
        block = {
            "index": len(self.chain) + 1,
            "timestamp":time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.last_block)  #chain[-1]表示最后一个数组元素（区块）
        }
        self.current_transactions = []                  #因为已经打包成区块了，所以当前交易就要清空
        self.chain.append(block)                        #把刚打包好的区块加入到链条中
        return block

    def new_transaction(self,sender,recipient,amount) -> int:      #新添加一个交易，返回所在的区块索引
        self.current_transactions.append(
            {
                "sender":sender,
                "recipient": recipient,
                "amount": amount,
            }
        )
        return self.last_block['index'] + 1

    @property
    def last_block(self):           #最后一个区块
        return self.chain[-1]

    @staticmethod
    def hash(block):                 #计算区块的哈希值
        block_string = json.dumps(block,sort_keys = True)       #将json转化为字符串数组
        return hashlib.sha256(block_string).hexdigest()            #得到摘要信息

        """
        简单的工作量证明:不停的尝试一个proof的值，看看这个值与上一个proof进行计算时是否满足以4个0开头，
        如果满足就返回这个proof的值，如果不满足就加1进行下一次验证运算
        
        """
    def proof_of_work(self, last_proof: int) -> int:
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头
        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

app = Flask(__name__)
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

#这个路由只是做测试的，没什么用
@app.route('/index', methods=['GET'])       #这是一个路由，可映射到一个方法
def index():
    return "Hello Blockchain"

@app.route('/transactions/new', methods=['POST'])   #这里用post请求，因为要上传数据
def new_transaction():
    values = request.get_json()
    # 检查POST数据
    required = ['sender', 'recipient', 'amount']

    if values is None:
        return 'Missing values', 400

    if not all(k in values for k in required):
        return 'Missing values', 400
    #返回的是所在区块的索引
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201           #通常post请求，添加一条记录都是返回201

@app.route('/mine', methods=['GET'])                #挖矿、哈西打包(1、先算工作量证明。2、给自己添加一个奖励的交易)
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']           #上一个块的工作量证明
    proof = blockchain.proof_of_work(last_proof)    #当前块的工作量证明

    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.new_transaction(
                                sender="0",
                                recipient=node_identifier,
                                amount=1)
    block = blockchain.new_block(proof, None)    #None为上一个区块的哈希值

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():                           #把当前的区块链信息返回给请求者
    response = {
        'chain':blockchain.chain,           #完整的区块链
        'length':len(blockchain.chain)
    }
    return jsonify(response),200    #jsonify可以把json转化为字符串。(http请求返回的应该是个字符串)

#{ "nodes":["http://127.0.0.2:5000"] }
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201           #POST的请求很多返回的是201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)          #0.0.0.0表示接受所有的ip
