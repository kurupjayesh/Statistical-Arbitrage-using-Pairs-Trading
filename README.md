#Statistical Arbitrage using Pairs Trading

By Jayesh Kurup

History of Statistical Arbitrage:

This strategy was first developed and used in the mid 1980s by Nunzio Tartaglia’s quantitative group at Morgan Stanly.

This is a mean reverting strategy to harness to behavior of similar securities

What is Pairs Trading:

Statistical arbitrage trading or pairs trading as it is commonly known is defined as trading one financial instrument or a basket of financial instruments.

The co-integrated pairs are usually mean reverting in nature viz after deviating from the mean, they tend to revert back at some point.

The farther the difference from the mean, greater is the probability of a reversal.

Note however that statistical arbitrage is not a risk free strategy. For example one of the position taken for a pair, may pick up a trend than reverting back to the mean. We should hence define strickt thresholds to ascertain we dont incur tremendous loss.

The Concept:

Step 1:  Find two securities that are in the same sector / industry, similar market capitalization and average volume traded is preffered. (Eg. Master Card (MA)/ Visa(V) ) 

Step 2: Calculate the spread, I have used the pair ratio to indicate the spread. It is simply the log of price of security A / price security B.

Step 3: Calculate the mean, standard deviation, and z-score of the pair ratio / spread and define strict thresholds for entry/exit

Step 4: Ensure securities are co integrated. I have used the Augmented Dicky Fuller Test (ADF Test) to test for co-integration. The test has to reject the null hypothesis that the pair is not co-integrated.

Step 5: Generate trading signals Trading signals are based on the z-score. In the project I have used a z-score of 2 and Stop Loss at 3, Take Profit at 0.5 (This can be varied and suited as per choice, see What If analysis in Excel for best combination)

Step 6: Process transactions based on signals

Step 7: Reporting

