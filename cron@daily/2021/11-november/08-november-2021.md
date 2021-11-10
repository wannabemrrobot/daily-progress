### Release - V1.6
#### Prevent loading older timelines, unless required.
This has made significant performance improvements in the application, as it now loads only the 10 lastest timeline events and it's respective markdowns from the github, which was not the case before.  
Previously, the application loads all the timeline events and its markdowns from the github. This had a significant impact on the performance particularly on low-end devices as it loads all the timeline events, even it contains 1000's of markdown entries.

#### To-do:
- Optimal solutions for LeetCode - 58, 441
- Bit manipulation using XOR
- Implement lazy loading in [@wannabemrrobot](https://wannabemrrobot.web.app)