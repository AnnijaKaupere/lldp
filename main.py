from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import SSHException
from netmiko.exceptions import AuthenticationException
import matplotlib.pyplot as plt
import networkx as nx

# here is list of switch ip address
ip_list = []
# '10.70.100.51'
addresses = str(input("Введите адреса через запятую без пробела: "))
split_addresses = addresses.split(",")
for i in split_addresses:
    ip_list.append(i)
print(ip_list)


# clearing the old data from the CSV file and writing the headers
f = open("login_issues.csv", "w+")
f.write("IP Address, Status")
f.write("\n")
f.close()

f = open("conf.csv", 'w').close()

n = open("neighbours.txt", "w+")
n.close()


def error_mes(mes):
    o = open("conf.csv", "a")
    o.write("\n\n----------------------IP_ADDRESS: ", )
    o.write(ip)
    o.write("----------------------")
    o.write("\n")
    o.write(mes)
    o.write("\n\n")
    o.close()


# для графа !!!!!!!!!!!
nodes = []
edges = []
# то что выше - для графа !!!!!!!!!!!!
k = 0
# loop all ip addresses in ip_list
for ip in ip_list:
    nodes.clear()
    edges.clear()

    eltex = {
        'device_type': 'eltex',
        'ip': ip,
        'username': str(input('username for '+ip+" : ")),  # ssh username
        'password': str(input('password : ')),  # ssh password
        'secret': 'admin',  # ssh_enable_password
        'ssh_strict': False,
        'fast_cli': False,
    }

    # handling exceptions errors

    try:
        net_connect = ConnectHandler(**eltex)

    except NetMikoTimeoutException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Device Unreachable/SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("Device Unreachable/SSH not enabled")
        print("Device Unreachable/SSH not enabled")
        continue

    except AuthenticationException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Authentication Failure")
        f.write("\n")
        f.close()
        error_mes("Authentication Failure")
        print(error_mes("Authentication Failure"))
        continue
    except SSHException:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "SSH not enabled")
        f.write("\n")
        f.close()
        error_mes("SSH not enabled")
        print(error_mes("SSH not enabled"))
        continue

    try:
        net_connect.enable()
        f = open("login_issues.csv", "a")
        f.write(ip + "," + " Connected")
        f.write("\n")
        f.close()

    # handling exceptions errors
    except ValueError:
        f = open("login_issues.csv", "a")
        f.write(ip + "," + "Could be SSH Enable Password issue")
        f.write("\n")
        f.close()
        error_mes("Could be SSH Enable Password issue")
        print(error_mes("Could be SSH Enable Password issue"))
        continue

    sh_lldp_output = net_connect.send_command('show lldp neighbors')
    sh_lldp1_output = net_connect.send_command('show lldp neighbors gi1/0/8')
    print(sh_lldp_output)
    f = open("conf.csv", "a")
    f.write("\n\n----------------------IP_ADDRESS: ")
    f.write(ip)
    f.write("----------------------\n\n-----lldp neighbors info-----\n")
    f.write(sh_lldp_output)
    f.write("----------------------\n\n-----lldp neighbors1/0/8 info-----")
    f.write(sh_lldp1_output)

    lldp_out = sh_lldp_output.split()
    print( lldp_out)
    interfaces = []

    for i in lldp_out:
        blacklist = ["Point;", "telephone;", "Port", "Ports", "System", "Repeater;", "Router;"]
        if i.__contains__('eltex'):
            blacklist.append(i)
        if (i.__contains__("gi") | i.__contains__("Po") | i.__contains__("te")) & (i not in blacklist):
            interfaces.append(i)
    print(interfaces, 'DO')
    del interfaces[1::2]
    print(interfaces, 'POSLE')
    print("------- ip address : ", ip, "-------")
    n = open("neighbours.txt", "a")
    n.write("\n\n------- ip address : ")
    n.write(ip)
    n.write("-------")
    nodes.append(ip)
    p = 1

    for interface in interfaces:

        sh_lldp = net_connect.send_command('show lldp neighbors ' + interface)
        sh = sh_lldp.splitlines()
        for line in sh:
            if line.__contains__("Management Address:"):
                print(line)
                int_ip = line.split()
                print(int_ip[2])
                if int_ip[2] not in ip_list:
                    ip_list.append(int_ip[2])

                print('\n', interface, "----->", int_ip[2])
                n = open("neighbours.txt", "a")
                n.write('\n')
                n.write(interface)
                n.write("----->")
                n.write(int_ip[2])
                nodes.append(int_ip[2])
                edges.append((nodes[k], nodes[p]))


        G = nx.DiGraph(directed=True)

        options = {
            'node_color': 'pink',  # color of node
            'node_size': 2600,  # size of node
            'width': 1,  # line width of edges
            'arrowstyle': '-|>',  # array style for directed graph
            'arrowsize': 30,  # size of arrow
            'edge_color': 'black',  # edge color
        }

        print(nodes)

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.draw(G, with_labels=True, font_weight='bold', **options)

        pos = nx.circular_layout(G)
        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels={
                                         (nodes[k], nodes[p]): interface
                                     },
                                     font_color='pink'
                                     )
        plt.show()
        print(nodes)
        print (k)
        print (p)
        print(edges, ' EDGESSSSSSSSS')
        p += 1


    # k += 1

input('press ENTER to exit')


# 10.70.100.51
# admin
# 10.70.100.38
# ahRUz!Sx
