# fortune500
This project aims to develop a model to analyse stock movements and analyse the correlation with quarterly reports - specifically for fortune 500 companies.

Some Descriptions of the data included:

**1. SEC Form 10-K (Annual Report)**

*   **What it is:** This is a company's **comprehensive annual report** filed with the Securities and Exchange Commission (SEC). It provides a detailed picture of the company's business, financial condition, and results of operations over the *entire fiscal year*.
*   **Key Characteristics:**
    *   **Frequency:** Filed once a year (usually 60-90 days after the company's fiscal year ends).
    *   **Scope:** Very detailed and comprehensive.
    *   **Audit:** Contains **audited** financial statements (audited by an independent accounting firm), providing higher reliability for the numbers.
*   **Key Sections to Interpret for Your Project:**
    *   **Item 1: Business:** Describes the company's main operations, products/services, markets, competition, strategy, and dependencies.
        *   *Interpretation:* Understand *what* the company does. Look for changes in strategy, new market entries/exits, or shifts in competitive landscape mentioned year-over-year (YoY).
    *   **Item 1A: Risk Factors:** The company outlines potential risks that could negatively impact its business or financial results (e.g., economic downturns, competition, regulations, operational issues, cybersecurity threats).
        *   *Interpretation:* **Crucial for qualitative analysis.** Track *changes* in risks YoY. Are new significant risks added? Are existing risks emphasized more? Are risks removed? Changes often signal evolving challenges or priorities. Quantify changes (e.g., number of new risks, similarity score of text YoY).
    *   **Item 7: Management's Discussion and Analysis (MD&A):** Management provides a narrative explaining the company's financial performance and condition during the year. They discuss trends, key performance indicators (KPIs), uncertainties, liquidity, capital resources, and often provide some **forward-looking statements** about their expectations.
        *   *Interpretation:* **Goldmine for NLP.** Analyze sentiment (optimism/pessimism), identify key themes discussed (e.g., growth drivers, cost control), extract forward-looking statements (guidance, expectations), quantify management tone. Compare the narrative to previous years. Does management sound more or less confident? Are they highlighting new opportunities or challenges?
    *   **Item 8: Financial Statements and Supplementary Data:** Contains the core audited financial statements: Balance Sheet, Income Statement, Statement of Cash Flows, Statement of Stockholders' Equity, and Notes to the Financial Statements.
        *   *Interpretation:* The "hard" numbers. Extract key metrics (Revenue, Net Income, EPS, Debt, Cash Flow). Calculate growth rates, margins, ratios (P/E, Debt-to-Equity). This is where XBRL parsing is very useful for accuracy. Compare trends YoY.
    *   **Notes to Financial Statements:** Provides critical details about the accounting policies used and breakdowns of line items in the main statements (e.g., debt details, segment information, acquisition impacts).
        *   *Interpretation:* Essential context for Item 8. Can reveal important details about revenue recognition, acquisitions, impairments, or off-balance-sheet items.

**2. SEC Form 10-Q (Quarterly Report)**

*   **What it is:** This is a company's **quarterly update**, providing a continuing view of its financial position and results during the year.
*   **Key Characteristics:**
    *   **Frequency:** Filed three times a year (usually 40-45 days after the end of each fiscal quarter). The fourth quarter's information is covered in the 10-K.
    *   **Scope:** Less detailed than the 10-K; focuses on updates since the last filing.
    *   **Audit:** Financial statements are generally **unaudited** or subject to limited review by auditors.
*   **Key Sections to Interpret for Your Project:**
    *   **Part I, Item 1: Financial Statements:** Condensed versions of the key financial statements (Balance Sheet, Income Statement, Cash Flow).
        *   *Interpretation:* Provides the latest quarterly performance snapshot. Compare to the same quarter last year (YoY comparison) and the previous quarter (QoQ comparison) to identify trends and short-term performance changes.
    *   **Part I, Item 2: Management's Discussion and Analysis (MD&A):** An updated narrative focusing on the results of the quarter and the year-to-date period. Discusses material changes from the last filing.
        *   *Interpretation:* Similar to 10-K MD&A but focused on the quarter. **Very important for timely signals.** Analyze sentiment, identify explanations for quarterly performance (beats/misses vs. expectations), find updated forward-looking statements or changes in outlook. Compare sentiment/topics QoQ and YoY.
    *   **Part I, Item 3: Quantitative and Qualitative Disclosures About Market Risk:** Updates on the company's exposure to market risks (like interest rates, foreign currency exchange).
        *   *Interpretation:* Note any significant changes in stated risk exposure.
    *   **Part II, Item 1A: Risk Factors:** Discloses any *material changes* to the risk factors previously reported in the most recent 10-K. Often, companies state there are "no material changes," but sometimes significant new risks emerge mid-year.
        *   *Interpretation:* Pay close attention if this section *does* contain updates, as new quarterly risks can be significant signals.

**How to Interpret Them Together for Market Correlation:**

1.  **Baseline:** Use the **10-K** to establish a baseline understanding of the company's business model, overall strategy, major risks, and annual performance trends.
2.  **Timely Updates:** Use the **10-Q** for more frequent updates on performance, management sentiment, and emerging risks/opportunities *during* the year. These are often more closely tied to short-term market reactions around earnings releases.
3.  **Focus on Change:** The market often reacts more to *changes* and *surprises* than absolute levels. Therefore, focus your analysis on:
    *   **QoQ and YoY Changes:** In financial metrics (revenue growth, margin changes).
    *   **Changes in Narrative:** Shifts in MD&A sentiment, new topics discussed, altered forward-looking guidance.
    *   **Changes in Risk Factors:** New or significantly modified risks mentioned in 10-Ks or 10-Qs.
4.  **Combine Quantitative & Qualitative:** Correlate the hard numbers (from Financial Statements) with the soft information (sentiment, risk changes, MD&A themes extracted via NLP). Does strong revenue growth align with positive sentiment? Does mention of a new risk precede market underperformance?
5.  **Context is Key:** Interpret findings within the context of the broader market, industry trends, and analyst expectations (if you incorporate that data later). A company might report decent growth, but if it's below expectations or peers are doing much better, the market reaction could still be negative.


**1. `market_data_close.csv`**

*   **What it is:** This file contains the **daily closing price** for each ticker.
*   **Interpretation:** This adjusted closing price represents the theoretically comparable value of the stock over time. If you bought a share years ago, this adjusted price accounts for how many shares you'd have now after splits and the value of dividends received (reinvested conceptually). It's the standard price used for calculating historical performance and returns accurately.
*   **Structure:**
    *   Rows: Indexed by Date (e.g., `2023-10-26`, `2023-10-27`, ...).
    *   Columns: Tickers (`AAPL`, `MSFT`, `AMZN`, `^GSPC`).
    *   Values: The adjusted closing price for that stock on that day (e.g., 170.50).

**2. `market_data_volume.csv`**

*   **What it is:** This file contains the **daily trading volume** for each ticker.
*   **Interpretation:** Volume represents the total number of shares of that stock that were traded during that specific day. High volume can indicate higher investor interest or conviction (either buying or selling). It's often analyzed alongside price movements. For the index (`^GSPC`), the volume typically represents the combined volume of the underlying stocks or related ETF volume, depending on how Yahoo Finance reports it.
*   **Structure:**
    *   Rows: Indexed by Date.
    *   Columns: Tickers (`AAPL`, `MSFT`, `AMZN`, `^GSPC`).
    *   Values: The number of shares traded for that stock on that day (e.g., 55,100,000).

**3. `market_data_daily_returns.csv`**

*   **What it is:** This file contains the calculated **daily percentage returns** for each ticker.
*   **How it was Calculated:** The script calculated this using the `pct_change()` method on the **adjusted closing prices** from `market_data_close.csv`. The formula for each day is essentially: `(Todays_Adjusted_Close - Yesterdays_Adjusted_Close) / Yesterdays_Adjusted_Close`.
*   **Interpretation:** This represents the daily gain or loss for each stock/index as a percentage. For example, a value of `0.015` means the stock increased by 1.5% that day, while `-0.005` means it decreased by 0.5%. This is often the data you'll directly use as a target variable (what you're trying to predict) or as features (e.g., momentum based on past returns).
*   **Structure:**
    *   Rows: Indexed by Date (Note: The very first date from the original download range will be missing here, as returns cannot be calculated without a previous day. The `.dropna()` command removed it).
    *   Columns: Tickers (`AAPL`, `MSFT`, `AMZN`, `^GSPC`).
    *   Values: The daily percentage return (e.g., `0.015`, `-0.005`).