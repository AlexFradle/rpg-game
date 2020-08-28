from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from dataclasses import dataclass


# @dataclass
# class Node:
#     element: object
#     parent: object
#
#
# def get_child(parent, route):
#     """Pre-Order Traversal"""
#     for child in parent.element:
#         if child not in [i.element for i in route]:
#             route.append(Node(child, parent.element))
#             get_child(Node(child, parent.element), route)
#     if parent == route[0]:
#         return route
#     if len(parent.element) == 0 or parent in route:
#         get_child(route[route.index(parent) - 1], route)
#
#
# tree = ElementTree.parse("skill_tree.xml")
# root = tree.getroot()
# x = get_child(Node(root, None), [Node(root, None)])

