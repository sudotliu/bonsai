# Bonsai

## Walker Node Positioning Algorithm (in Python)

Bonsai is a tree positioning utility that can compute coordinates for all nodes in a given tree such
that they are neatly and evenly spaced out when displayed visually. The original use-case was to
enable recomputing the node positions for a dynamic tree to be rendered in a web application, so
anything similar may benefit from this. Pretty much anything that involves displaying a tree
structure that changes in shape often enough to make it cumbersome to reposition or balance by hand.

Here is an example image of the original use-case:
![Bonsai Metric Tree Example](bonsai_example_big.png)

The core of this project is a Python implementation of John Q. Walker II's node-positioning
algorithm for general trees with some adjustments, additional methods, and wrapper layers to provide
a better user interface. It is a recursive algorithm but for reasonably-sized trees, node placements
are recalculated quickly enough to support instant re-rendering of the tree upon adding or removing
nodes.

Included is the original report that describes the algorithm, provided by the University of North
Carolina:\
<a href="89-034.pdf" target="_blank">A Node-Positioning Algorithm for General Trees</a>

Note: there are select comments marked specifically with `NB` (nota bene), which call to attention
parts of the algorithm that differ from the original specification because something did not work as
expected without those changes. The majority of the internal logic (`walker_tree.py`) should
otherwise be largely as prescribed in the report.

While I plan to give this project an MIT license, it is currently pending response from the
copyright owners so anyone seeking to use this software, especially for commercial purposes, should
refer to the <a href="https://policies.unc.edu/TDClient/2833/Portal/KB/ArticleDet?ID=132138"
target="_blank">policies published by UNC</a> and reach out to them directly to request licensing
for this project.
