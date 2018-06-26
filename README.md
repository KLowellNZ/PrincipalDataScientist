# PrincipalDataScientist
Applicant: Kim Lowell

Files in this repository address some of my contributions to a team-based
project; see description of “Arkatechture” in my cv.  The goal of the
project was to use publicly available data on financial institutions – 
banks and credit unions – to rapidly show their current state and historical
performance relative to their peer institutions.  (Financial institutions
define their peers by size and the state in which they are located.)

Most of the files are Python Spyder files that address various aspects of the 
project – e.g., using scikit-learn to fit regressions, utility programs for data 
formatting and joining, etc

-- NCUA_KPI_SummaryStats.py  The 12 KPIs used in this project were chosen
  from 96 candidate KPIs.  This program calculates all 96 for 6,000 credit
  unions and then calculates summary statistics to provide information about
  the variability and frequency distributions of the KPIs.

-- NCUA_PYE_KPIs_for_NCUAs.py  This calculates 12 financial KPIs for 6,000 
  credit unions for a desired year and outputs them to a csv file for
  subsequent analysis.  A comparable program for banks (whose KPIs are
  calculated differently) was also produced.

-- FDIC_Redshift_SQL_Connect_plus_KPI.ipynb (Jupyter notebook) Ultimately,
  financial institution data were stored in the cloud using Amazon Web
  Services Redshift. This program uses Python to connect to AWS Redshift,
  generate SQL to extract the data requested for a given year and 12 KPIs,
  calcualtes the KPIs, and outputs them to a csv file.

-- Get_FI_Neighbours.py   For a subject bank/credit union, this program identifies
  the two nearest-neighbour banks and credit unions defined by being in the
  same state as the subject, and having the shortest Euclidean distance to
  the subject based on total value of loans and total value of deposits.

-- Join2013_14_15_16_17_KPIs.py  A utility program to combine data for some
  12,000 financial institutions for 5 different years residing in 5 files
  into a single file for analysis using scikit-learn.

-- NCUA_FDIC_KPIRegression_CUs_and_Banks.py  Using scikit-learn, a regression
  trendline is fit through 5-year data for some 12,000 financial institutions
  for 12 key performances indicators.  The slope of the regression line is
  used to show trend of a financial institution and the inverse of r-squared
  indicates volatility in the Tableau dashboard included in this github
  repository.

-- TransposeKPIs.py  To produce various visualisations of the KPIs, data
  had to be reformatted.  This utility program does one such re-formatting
  of multi-temporal data.

-- CUandBanks_2013-17_Regr_Viz.twbx  This is a Tableau file showing the
  interactive dashboard created to show financial institutions their 5-year
  trend and volatility for four major financial categories (e.g., Earnings,
  Capital Adequacy). The dashboard also allows financial institutions to
  compare their performance against their peer institutions and displays
  their two closest peer banks and two closest peer credit unions.

Available upon request are additional samples of Python or R that address other 
machine learning and analytical techniques including web-scraping, text analysis, 
deep learning (using keras), time series analysis, and others.
