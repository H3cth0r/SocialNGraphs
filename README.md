# Social Network Graphs
The purpose of the repository is to explore the structures 
of social network relationships.

The initial objective is to retrieve all followers and following 
users of the target user. For each of the user's "friends," 
obtain their followers and following. Users with more than 4000 
followers or following will be excluded, and verified users will 
also be skipped. The limit of users to iterate per user will 
be set at 1000 for subsequent users, not including the target user.


The current idea is to create a second method with the inten-
tion of applying pareto distribution, to capture as much
communities as posible.

## Leopard 
The main idea of Leopard is to reach as much communities as possible
of a target user. It will be based in the pareto distribution.
The main idea is to take a random pick of 20% of the users friends or
followers list. This will enable the to capture communities in a more 
effient way. 


## TODO
- Create queue of unvisited profiles
- Iterate over followers
- Iterate over all the followers and following
