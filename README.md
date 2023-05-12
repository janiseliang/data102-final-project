# Analysis of Chronic Diseases and Air Quality

This repository contains code for our Data 102 Final Project.

**Group:** Janise Liang, Eduardo Madrigal, Sheryl Muttath, and Nandita Radhakrishnan

## Introduction

We evaluated two research questions, which has been split up into separate analysis notebooks:

1. `analysis/question1.ipynb`: Correlation between diabetes prevalence and various health-affecting factors such as exercise, obesity, and age.
   Used methods for multiple hypothesis testing, including correcting for False Discovery Rates (FDR) with Bonferroni correction, and Family-Wise Error Rates (FWER) with Benjamini-Yekutieli.
2. `analysis/question2.ipynb`: Causal effect (if any) of PM 2.5 concentration on COPD (chronic obstructive pulmonary disease) prevalence.
   Used methods for causal inference using inverse-propensity weighting (IPW) on smoking, a confounding variable.

## Installation

Install all required packages to run the notebooks using `pip install -r requirements.txt`.

* This includes an API package called sodapy for downloading CDC data.
