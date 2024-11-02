import numpy as np

MAX = float('inf')  # 定义常量 MAX 表示无穷大，用于表示图中的不可达路径

# Dijkstra 算法实现：用于寻找给定起点到所有其他顶点的最短路径
def dijkstra(self, source):
    # 初始化距离列表，所有顶点距离初始化为 MAX，起始顶点的距离设置为 0
    dist = [MAX] * self.vertexNum
    visited = [False] * self.vertexNum  # 记录每个顶点是否已被访问
    previous = [[]] * self.vertexNum  # 保存路径的前驱节点

    dist[source] = 0
    Q = set([source])  # 未访问节点的集合，初始包含起点

    while len(Q) > 0:
        # 查找未访问节点中距离最小的节点 u
        seq = -1
        smallest = MAX
        for q in Q:
            if visited[q] == False:
                if dist[q] < smallest:
                    smallest = dist[q]
                    seq = q
        u = seq

        Q.remove(u)  # 从未访问集合中移除节点 u
        visited[u] = True  # 标记 u 为已访问

        # 遍历与 u 相邻的所有节点 v，更新路径距离
        for v in range(self.vertexNum):
            if self.graph[u][v] < MAX:  # 检查节点 u 和 v 是否相连
                alt = dist[u] + self.graph[u][v]  # 计算新的距离 alt
                if alt < dist[v]:  # 如果找到更短的路径，更新距离和前驱节点
                    dist[v] = alt
                    previous[v] = []
                    previous[v].append(u)
                elif alt == dist[v]:  # 如果有相同长度的路径，添加到前驱节点列表中
                    if len(previous[v]) == 0 or u != v:
                        previous[v].append(u)
                if not visited[v]:  # 如果节点 v 未访问，添加到未访问集合
                    Q.add(v)

    return dist, previous  # 返回起点到每个节点的最短距离和前驱节点

# dijk 函数的另一个实现版本
def dijk(graph, starter):
    dist = [MAX] * len(graph)
    visited = [False] * len(graph)
    previous = [[]] * len(graph)
    dist[starter] = 0
    routes = [[]] * len(graph)
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

# dijkstra_path 类：包含 Dijkstra 算法的实现，能找到从起点到各个节点的最短路径
class dijkstra_path():
    def __init__(self, graph, src_vertex):
        self.graph = graph
        self.src_vertex = src_vertex
        self.set = self.get_set()  # 已访问节点集合
        self.unsearch = self.get_unsearch()  # 未访问节点集合
        self.dis = self.get_dis()  # 从起点到每个节点的初始距离
        self.path = self.get_path()  # 路径信息
        self.point = self.get_point()  # 当前正在处理的节点

    # 初始化访问集合，包含起点
    def get_set(self):
        return [self.src_vertex]

    # 初始化未访问集合
    def get_unsearch(self):
        unsearch = []
        for i in range(len(self.graph)):
            unsearch.append(i)
        unsearch.remove(self.src_vertex)
        return unsearch

    # 初始化距离信息
    def get_dis(self):
        dis = {}
        vertexs = []
        for i in range(len(self.graph)):
            vertexs.append(i)
        index = vertexs.index(self.src_vertex)
        for i, distance in enumerate(self.graph[index]):
            dis[vertexs[i]] = distance
        return dis

    # 初始化路径信息
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

    # 返回当前处理的节点
    def get_point(self):
        return self.src_vertex

    # 更新当前点到其他节点的最小距离
    def update_point(self, index):
        dis_sort = list(self.dis.values())
        dis_sort.sort()
        point_dis = dis_sort[index]
        for key, distance in self.dis.items():
            if distance == point_dis and key not in self.set:
                self.point = key
                break

    # 更新路径信息
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
                self.path[key] = self.path[self.point].copy()
                self.path[key].append(self.point)

    # 查找从起点到目标节点的最短路径
    def find_shortestPath(self, dst_vertex=None, info_show=False):
        count = 1
        if info_show:
            print('*' * 10, 'initialize', '*' * 10)
            self.show()
        while self.unsearch:
            self.update_point(count)
            self.set.append(self.point)
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

    # 显示当前算法的状态信息
    def show(self):
        print('set:', self.set)
        print('unsearch:', self.unsearch)
        print('point:', self.point)
        print('dis:', self.dis.values())
        print('path:', self.path.values())

# 另一个最短路径算法的实现
def startwith(start: int, mgraph: list):
    passed = [start]  # 已访问的节点列表
    nopass = [x for x in range(len(mgraph)) if x != start]  # 未访问节点列表
    dis = mgraph[start]  # 从起始节点到其他节点的距离

    # 为相邻节点初始化路径信息
    dict_ = {}
    for i in range(len(dis)):
        if dis[i] != MAX:
            dict_[str(i)] = [start]

    while len(nopass):
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

# 示例图和调用代码
if __name__ == '__main__':
    graph = [
        [0, MAX, MAX, 1, 1, 1],
        [MAX, 0, MAX, 1, 1, 1],
        [MAX, MAX, 0, 1, 1, 1],
        [1, 1, 1, 0, MAX, MAX],
        [1, 1, 1, MAX, 0, MAX],
        [1, 1, 1, MAX, MAX, 0],
    ]
    mgraph = [
        [0, 1, 12, MAX, MAX, MAX],
        [1, 0, 9, 3, MAX, MAX],
        [12, 9, 0, 4, 5, MAX],
        [MAX, 3, 4, 0, 13, 15],
        [MAX, MAX, 5, 13, 0, 4],
        [MAX, MAX, MAX, 15, 4, 0]
    ]

    # 测试 dijkstra