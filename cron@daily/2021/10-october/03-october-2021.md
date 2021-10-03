### Implemented Circular LinkedList
Vanilla Implementation of Circular LinkedList, where there are two variables namely `first` and `last` to keep track of the first and last positions in the list.

#### Insights:
- The variables `first` and `last` are not actually referring to the positions itself.
- Those variables are just a reference for the nodes in the first and the last positions to keep track of the nodes.
- In other words, they are not like indexes and more of a stack pointers.
- `deleteLastNode()` method is not implemented as it involves traversing through the entire list to keep track of the `second last node`, to set its `next` variable to the first(CLL).

#### Reference:
- [Java Implementation of Circular Linkedlists](https://github.com/wannabemrrobot/becoming-leet/tree/main/courseworks/practical-data-structures-algorithms-in-java/eclipse-workspace/becoming-leet/src/ds/circularlinkedlist)