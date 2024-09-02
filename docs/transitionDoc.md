### Project description

lightDSO aims to integrate dynamic illumination information into the DSO algorithm, with the hope of achieving better tracking in dark environments with mono and stereo vision. This information integration is achieved by incorporating a simple lighting model (characterized by the lighting position and intensity) into the pixel intensity calculations.

### Project structure and pointers

The main changes for this work were made in the Residuals.cpp file, lines 198-204 at the current moment. This line does the calculations related to the simple illumination model and integrates it into the residual calculation.

Many useful scripts for testing, dataset preparation, and evaluation are located in the helpfulScripts and evaluation_tools folders. pipeline.py in particular generates the graphs and other statistics used in the thesis defense.

The desktop machine this work is currently set up on is in the lab. Ask Chris for the login details. It should already be set up to run the program, with the datasets downloaded and available.

### Next steps

The thesis defense provided proof of concept, but a lot more needs to be done to prove that the novel method is an improvement. Here are some next steps:

- Test the program over OIVIO dataset instead of synthetic data
- Tune hyperparameters for better performance
- Test over many more iterations of the program for better data
- Deep dive on tracking failures to find areas for potential improvement
