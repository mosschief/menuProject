__author__ = 'mossc'





def create_tour(nodes):
    my_list = []

    length = len(nodes)
    i = 0
    while i < length-1:

            pair = [nodes[i],nodes[i+1]]
            my_list.append(pair)
            i += 1

    my_list.append([nodes[length-1],nodes[0]])

    return my_list

z=2
for j in range(4):
    z += 1
    for