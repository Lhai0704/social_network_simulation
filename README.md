# social_network_simulation
## 社交网络模拟系统
LLM驱动节点

fastapi作为后端框架。MySQL数据持久化。
ollama本地LLM，llama3.1

## 安装
创建config.py文件，输入
MYSQLPASSWORD = 'YOUR_PASSWORD'
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:" + MYSQLPASSWORD + "@localhost/social_network_simulation"

## 基本操作
### 添加节点
curl -X POST "http://localhost:8000/nodes/" -H "Content-Type: application/json" -d '{"name": "Amy"}'
### 添加节点连接
curl -X POST "http://localhost:8000/nodes/1/connect" \
-H "Content-Type: application/json" \
-d '{"target_node_id": 2}'
### 对话
curl -X POST "http://localhost:8000/start-dialogue/?node1_id=1&node2_id=2&num_turns=5"


参考资料：
