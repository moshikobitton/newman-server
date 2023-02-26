##
import json

import pymssql as pymssql
from flask import Flask, request
from flask_cors import CORS
import networkx as nx

app = Flask(__name__)
cors = CORS(app)


def getCommunitiesNewmanData(data, nodesDict):
    # Create an empty graph
    G = nx.Graph()

    # Add nodes and links to the graph
    for k in nodesDict:
        G.add_node(nodesDict.get(k), name=k)
    for row in data:
        G.add_edge(nodesDict[row[0]], nodesDict[row[1]], strength=row[4])

    communities = nx.algorithms.community.greedy_modularity_communities(G)
    modularityNum = nx.algorithms.community.modularity(G, communities)

    # Print the communities
    G.nodes()
    nodes = []
    edges = []
    response = {"data": {"nodes": [], "edges": []}, "modularity": modularityNum}
    for i in range(len(communities)):
        for cou in communities[i]:
            nodes.append({"id": cou, "name": G.nodes[cou]['name'], "color": i})

    for s, t, v in G.edges(data='strength'):
        edges.append({"from": s, "to": t, "value": v})
    response.get('data')['nodes'] = nodes
    response.get('data')['edges'] = edges
    return response


@app.route('/newman', methods=['POST'])
def getNewmanCommunities():
    conn = pymssql.connect(server='Media.ruppin.ac.il', user='igroup101', password='igroup101_69556',
                           database='igroup101_prod')
    cursor = conn.cursor()
    # Call the stored procedure
    stored_proc_name = 'spGetAllCountries'
    cursor.callproc(stored_proc_name)
    rows = cursor.fetchall()
    nodesDict = {}
    # Loop through the tuples in the array
    for tup in rows:
        # Add the key-value pair to the dictionary
        nodesDict[tup[1]] = tup[2]

    stored_proc_name = 'spReadTradesByInd&Year'
    ind = request.json.get('ind')
    year = request.json.get('year')
    cursor.callproc(stored_proc_name, (ind, year))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    newmanData = getCommunitiesNewmanData(data, nodesDict)
    # Process the resultset or return a message
    return json.dumps(newmanData)


# Close the connection and cursor

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
