from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics import DistanceMetric
from sklearn.cluster import AgglomerativeClustering
import seaborn as sns
from bokeh.palettes import viridis
import networkx as nx

#document embeddings
embedder=SentenceTransformer('allenai/specter')

corpus=df_nlp_filtered['papers'].values.tolist()
corpus_embeddings = embedder.encode(corpus)

#distance measures
dist = DistanceMetric.get_metric('euclidean')
dist_scores=dist.pairwise(corpus_embeddings)
all_scores=dist_scores[np.triu_indices(dist_scores.shape[0], 1)]

#visualizing the distance measures
sns.set(rc={"figure.figsize":(12, 6)}) #width=12, #height=8
sns.histplot(all_scores,bins=100000)

#clustering
clustering = AgglomerativeClustering(n_clusters=None,affinity='euclidean',distance_threshold=25).fit(corpus_embeddings)
clusters = clustering.labels_

#np.unique(clusters).shape[0]
#get the list of papers corresponding to each cluster
idx_sort = np.argsort(clusters)
sorted_clusters = clusters[idx_sort]

# returns the unique values, the index of the first occurrence of a value, and the count for each element
vals, idx_start, count = np.unique(sorted_clusters, return_counts=True, return_index=True)
# splits the indices into separate arrays
clusters_split = np.split(idx_sort, idx_start[1:])

#create a dict which will be used as attribute for the network of nodes
color_options_clust=viridis(len(clusters_split))

cluster_num = {}
node_title = {}
color_clust={}
#Loop through each community in the network
for cluster_number, cluster in enumerate(clusters_split):
    #For each member of the community, add their community number and a distinct color
    for node in cluster: 
        if node not in cluster_num.keys():
            cluster_num[node] = cluster_number
            node_title[node] = df_nlp_filtered.iloc[node]['title']
            color_clust[node] = color_options_clust[cluster_number]
            
#get a threshold for edges
avg_dist_score=np.zeros(len(clusters_split))
for j,clust in enumerate(clusters_split):
    clust_dist_score=0
    for i in range(len(clust)-1):
        node1=clust[i]
        node2=clust[i+1]
        clust_dist_score+=dist_scores[node1][node2]
    avg_dist_score[j]=clust_dist_score/len(clust)
    
threshold_graph=np.round(avg_dist_score.mean()+0*avg_dist_score.std(),2)

dist_scores_graph=dist_scores.copy()
dist_scores_graph[[dist_scores_graph <= threshold_graph]]=1
dist_scores_graph[[dist_scores_graph > threshold_graph]]=0

#create a network
G = nx.from_numpy_matrix(dist_scores_graph)

#add attributes
nx.set_node_attributes(G, cluster_num, 'cluster_num')
nx.set_node_attributes(G, node_title, 'node_title')
nx.set_node_attributes(G, color_clust, 'color_clust')

degrees = dict(nx.degree(G))
nx.set_node_attributes(G, name='degree', values=degrees)

#special functions for querying the network graph
def make_node_dict_for_cluster(cluster_num,clusters_split,G):
    node_dict={}
    for node in clusters_split[cluster_num]:
        node_dict[node]={}
        neighbors=[n for n in G.neighbors(node)]
        neighbor_cluster=[G.nodes[n]['cluster_num'] for n in G.neighbors(node)]
        node_dict[node]['neighbors']=np.array(neighbors)
        node_dict[node]['neighbor_cluster']=np.array(neighbor_cluster)

    return node_dict
    
 
def connections_with_cluster(node_dict,clust_num):
    nodes=list(node_dict.keys())
    clust_array=node_dict[nodes[0]]['neighbor_cluster']
    node_array=node_dict[nodes[0]]['neighbors']
    for node in nodes[1:]:
        np.hstack([clust_array,node_dict[node]['neighbor_cluster']])
        np.hstack([node_array,node_dict[node]['neighbors']])
    return np.count_nonzero(clust_array == clust_num),np.unique(node_array[clust_array == clust_num])
    
#node dictionary for cluster 3
dict_node_3=make_node_dict_for_cluster(3,clusters_split,G)
#getting its relatedness with cluster 10
connections_with_cluster(dict_node_3,10)
   
   #most central nodes of the network and least central 
   #(not to be confused with importance)
   #it gives information on intra network connectedness
   
def get_most_central_nodes(G,clust_num,top_k,bottom_k=False,clusters_split=clusters_split):
    G_new=G.subgraph(clusters_split[clust_num])
    sorted_dict=dict(sorted(nx.closeness_centrality(G_new).items(), key=lambda item: item[1],reverse=True))
    if bottom_k:
        return list(sorted_dict.keys())[-top_k:]
    return list(sorted_dict.keys())[0:top_k]
    
get_most_central_nodes(G,3,5,clusters_split=clusters_split)
   