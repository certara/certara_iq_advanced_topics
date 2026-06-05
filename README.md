# Overview

This project is designed to demonstrate the use of advanced methods in IQ. To facilitate the implementation of advanced methods, a local utilities folder has been generated.
If you are loading this project through a github link, then the utilities have been set up correctly. If you are recreating these methods in your own project, then you must recreate a utilities
folder with the same file structure and set up the utilities folder as a local utility within the project dependencies section.

# Methods

1. Advanced Templating in text based models

# Files

1. Templated_Model
   - `Build_Template.ipynb`: Walk through of how to generate a templated text based model file and how to develop a rendered model from this template. The model template exists as a string within this file
   - `model.txt`: Resultant model file from the walk through notebook saved as a text file
   - `Render_Template.ipynb`: Example of reading in a prebuilt template text file and rendering it
   - `advanced_templated.model`: Prebuilt template model file used as input to Render_Template.ipynb
   - `advanced_rendered.model`: Rendered version of the templated model

2. Uncertainty_Analysis
   - `uncertainty_analysis_tutorial.ipynb`: Tutorial notebook demonstrating uncertainty analysis methods in IQ
   - `two_compartment_pk_antibody.txt`: Two-compartment PK antibody model file used in the tutorial

3. Virtual_Populations
   - `VPop_inference.ipynb`: Tutorial notebook for virtual population inference using a cancer immunity cycle model with anti-PD1 treatment
   - `CIC_v4.2.0.iqd`: Cancer Immunity Cycle model file (open in IQ Design)
   - `parameters.csv`: Parameter table for the virtual population
   - `Calibrated_VPop.csv`: Calibrated virtual population output
   - `KEYNOTE001_waterfall_plot.csv`: Clinical data (KEYNOTE-001 trial waterfall plot) used for VPop calibration
   - `NSCLC_TME_composition.csv`: NSCLC tumor microenvironment composition data used for VPop inference
   - `README.md`: Setup instructions and tutorial overview

4. Troubleshooting
   - `README.md`: Guide covering common warnings, errors, and performance issues with `abm.simulate` and `abm.optimize`, including diagnostic strategies and recommended fixes