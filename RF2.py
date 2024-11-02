import numpy as np

MAX = float('inf')


def dijkstra(self, source):
    dist = [MAX] * self.vertexNum
    visited = [False] * self.vertexNum
    previous = [[]] * self.vertexNum

    dist[source] = 0
    Q = set([source])

    while len(Q) > 0:
        seq = -1
        smallest = MAX
        for q in Q:
            if visited[q] == False:
                if dist[q] < smallest:
                    smallest = dist[q]
                    seq = q
        u = seq

        Q.remove(u)
        visited[u] = True

        for v in range(self.vertexNum):
            if self.graph[u][v] < MAX:
                alt = dist[u] + self.graph[u][v]
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = []
                    previous[v].append(u)
                elif alt == dist[v]:
                    if len(previous[v]) == 0 or u != v:
                        previous[v].append(u)
                if not visited[v]:
                    Q.add(v)

    return dist, previous

def dijk(graph,starter):
    dist= [MAX]*len(graph)
    visited = [False] * len(graph)
    previous = [[]] * len(graph)
    dist[starter]=0
    routes=[[]]*len(graph)
    Q = {starter}
    while len(Q) > 0:
        seq = -1
        smallest = MAX
        for q in Q:
            if visited[q] == False:
                if dist[q] < smallest:
                    smallest = dist[q]
                    seq = q
        u = seq

        Q.remove(u)
        visited[u] = True

        for v in range(len(graph)):
            if graph[u][v] < MAX:

                alt = dist[u] + graph[u][v]
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = []
                    previous[v].append(u)
                    routes.clear()
                    routes[u][v].append(u)
                elif alt == dist[v]:
                    if len(previous[v]) == 0 or u != v:
                        previous[v].append(u)
                if not visited[v]:
                    Q.add(v)
    return dist, previous


class dijkstra_path():
    def __init__(self, graph, src_vertex):
        self.graph = graph
        self.src_vertex = src_vertex
        self.set = self.get_set()
        self.unsearch = self.get_unsearch()
        self.dis = self.get_dis()
        self.path = self.get_path()
        self.point = self.get_point()

    def get_set(self):
        return [self.src_vertex]

    def get_unsearch(self):
        unsearch = []
        for i in range(len(self.graph)):
            unsearch.append(i)
        unsearch.remove(self.src_vertex)
        return unsearch

    def get_dis(self):
        dis = {}
        vertexs=[]
        for i in range(len(self.graph)):
            vertexs.append(i)
        index = vertexs.index(self.src_vertex)
        for i, distance in enumerate(self.graph[index]):
            dis[vertexs[i]] = distance
        #print(dis)
        return dis

    def get_path(self):
        path = {}
        vertexs = []
        for i in range(len(self.graph)):
            vertexs.append(i)
        index = vertexs.index(self.src_vertex)
        for i, distance in enumerate(self.graph[index]):
            path[vertexs[i]] = []
            if distance != MAX:
                path[vertexs[i]].append(self.src_vertex)
        return path

    def get_point(self):
        return self.src_vertex


    #firstly find next node by dis index and set
    def update_point(self, index):
        dis_sort = list(self.dis.values())
        dis_sort.sort()
        point_dis = dis_sort[index]
        for key, distance in self.dis.items():
            if distance == point_dis and key not in self.set:
                self.point = key
                break
    #if dis>point dis+dis from point to every node ,then update
    def update_dis_path(self):
        new_dis = {}
        vertexs = []
        for i in range(len(self.graph)):
            vertexs.append(i)
        index_point = vertexs.index(self.point)
        for i, key in enumerate(self.dis.keys()):
            new_dis[key] = self.dis[self.point] + self.graph[index_point][i]
            if new_dis[key] < self.dis[key]:
                self.dis[key] = new_dis[key]
                #self.path[key] = self.path[self.point].append(self.point)
                self.path[key] = self.path[self.point].copy()
                self.path[key].append(self.point)

    def find_shortestPath(self, dst_vertex=None, info_show=False):
        count = 1
        if info_show:
            print('*' * 10, 'initialize', '*' * 10)
            self.show()
        while self.unsearch:
            self.update_point(count)
            self.set.append(self.point)
            # self.unsearch.remove(self.point)
            self.update_dis_path()
            if info_show:
                print('*' * 10, 'produce', count, '*' * 10)
                self.show()
            count += 1
            if dst_vertex != None and dst_vertex in self.set:
                result = self.path[dst_vertex].copy()
                result.append(dst_vertex)
                return result
        return self.path

    def show(self):
        print('set:', self.set)
        print('unsearch:', self.unsearch)
        print('point:', self.point)
        print('dis:', self.dis.values())
        print('path:', self.path.values())


def startwith(start: int, mgraph: list):
    # print(len(mgraph))
    passed = [start]
    nopass = [x for x in range(len(mgraph)) if x != start]

    dis = mgraph[start]
    # 创建字典 为直接与start节点相邻的节点初始化路径
    dict_ = {}
    for i in range(len(dis)):
        if dis[i] != MAX:
            dict_[str(i)] = [start]
            # print("link to ",i)
        # else:
        #     dict_[str(i)] = [MAX]

    while len(nopass):
        # print("last:",nopass)
        idx = nopass[0]
        for i in nopass:
            if dis[i] < dis[idx]:
                idx = i
        nopass.remove(idx)
        passed.append(idx)

        for i in nopass:
            if dis[idx] + mgraph[idx][i] < dis[i]:
                dis[i] = dis[idx] + mgraph[idx][i]
                dict_[str(i)] = dict_[str(idx)] + [idx]
    return dis, dict_




if __name__ == '__main__':
    graph = [
        [0, MAX, MAX, 1, 1, 1],
        [MAX, 0, MAX, 1, 1, 1],
        [MAX, MAX, 0, 1, 1, 1],
        [1, 1, 1, 0, MAX, MAX],
        [1, 1, 1, MAX, 0, MAX],
        [1, 1, 1, MAX, MAX, 0],
    ]
    mgraph = [[0 , 1, 12, MAX,  MAX,  MAX],
              [1, 0, 9, 3,  MAX,  MAX],
              [12, 9, 0, 4, 5, MAX],
              [MAX,3, 4, 0, 13, 15],
              [MAX,MAX,5,13,0,4],
              [MAX,MAX,MAX,15,4,0]]

    di=dijkstra_path(graph,0)
    for i in range(6):
        a = di.find_shortestPath(i)
        # print(a)
        # print(type(a))
        for j in range(len(a)):
            print(a[j],end=' ')
        print()
    # for i in range(6):
    #     a,B=startwith(i,mgraph)
    #
    #     # BB=B[str(0)]+[1]
    #
    #     print(a,B)
