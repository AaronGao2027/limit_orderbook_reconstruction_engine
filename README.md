# Limit Orderbook Reconstruction Engine

A low-latency limit orderbook reconstruction engine consolidating market by order data from 14 equity exchanges.

Following the Nasdaq TotalView-ITCH 5.0 documentation on the matching logic behind the matching engine, L3 MBO data from Databento is downloaded and stored as parquet files in a datalake. Reconstruction of specific securities over custom time periods showcase liquidity levels from each exchange at a tick by tick granularity.

This is a snapshot of the limit orderbook showcasing the bid and ask depths of 14 independent orderbooks from different equity exchanges and the central limit orderbook. 
 
The historical MBO data used in this analysis covers the entire trading day of the SPY ETF on March 23, 2026 (2026-03-23). It is stored in a parquet file that is too big to upload to Github (2.31 GB). I have uploaded the parquet file to a google drive and attached a link that can be used to access the shared google drive and download the parquet file. Using the parquet file, all the results generated in this project are reproducible on a local machine.

Google Drive Link: https://drive.google.com/drive/folders/1ZT-B_1j5lv2YSTIGm1_k5PmDqFLXIzhd?usp=sharing
