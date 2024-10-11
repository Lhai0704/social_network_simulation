import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Graph from './Graph';

const App = () => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
  axios.get('http://localhost:8000/nodes/')
    .then(response => {
      const nodeData = response.data.map(node => ({
        id: node.id,
        label: node.name
      }));

      const edgeData = [];
      response.data.forEach(node => {
        node.connections.forEach(connection => {
          edgeData.push({
            from: node.id,
            to: connection
          });
        });
      });

      setNodes(nodeData);
      setEdges(edgeData);
    })
    .catch(error => {
      console.error("There was an error fetching the data:", error);
    });
}, []);


  return (
    <div className="App">
      <h1>Social Network Visualization</h1>
      <Graph nodes={nodes} edges={edges} />
    </div>
  );
};

export default App;
