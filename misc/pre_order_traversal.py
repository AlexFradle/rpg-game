# from xml.etree import ElementTree
# from xml.etree.ElementTree import Element
# from dataclasses import dataclass
#
#
# @dataclass
# class Node:
#     element: object
#
#
# def get_child(parent, route):
#     """Pre-Order Traversal"""
#     for child in parent.element:
#         if child not in [i.element for i in route]:
#             route.append(Node(child))
#             get_child(Node(child), route)
#     if parent == route[0]:
#         return route
#
#
# tree = ElementTree.parse("skill_tree.xml")
# root = tree.getroot()
# pre_order = get_child(Node(root), [Node(root)])
#
# for i in pre_order:
#     print(i.element.tag)

class A:
    def __init__(self, x):
        self.__x = x


a = A(1)
print(a.__x)
