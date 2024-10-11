import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

const Graph = ({ nodes, edges }) => {
  const networkRef = useRef(null);

  useEffect(() => {
    console.log("Nodes:", nodes); // 调试：检查节点数据
    console.log("Edges:", edges); // 调试：检查边数据

    const container = networkRef.current;

    if (container && nodes.length > 0) { // 确保节点数据存在
      const data = { nodes, edges };
      const options = {
        nodes: {
          shape: "dot",
          size: 16,
        },
        edges: {
          arrows: "to",
        },
      };

      new Network(container, data, options);
    }
  }, [nodes, edges]);

  return <div ref={networkRef} style={{ height: '500px', border: '1px solid black' }} />;
};

export default Graph;
