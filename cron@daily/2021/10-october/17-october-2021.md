### Kadane's algorithm for Maximum Subarray Sum

The [Best Kadane's Algorithm explanation](https://medium.com/@rsinghal757/kadanes-algorithm-dynamic-programming-how-and-why-does-it-work-3fd8849ed73d) out there.  
My previous solution has O(n^2) TC, but this one has O(n) TC.

#### Insights:
- The best way to solve a problem is to `dry run` the program using paper and pen, atleast for me.
- Kadane's algorithm one liner:
  - `localMaximum[i] = max(Array[i], localMaximum[i-1] + Array[i])` 
- `Dynamic Programming` is a way to solve a problem by finding the sub problems in it, solving them and reusing the results wherever the recomputation of sub problem is needed.

#### Reference:
- [Kadane's Algorithm](https://medium.com/@rsinghal757/kadanes-algorithm-dynamic-programming-how-and-why-does-it-work-3fd8849ed73d)
- [Explain Dynamic Programming like am 4](https://www.quora.com/How-should-I-explain-dynamic-programming-to-a-4-year-old/answer/Jonathan-Paulson)