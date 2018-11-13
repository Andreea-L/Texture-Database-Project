# Creating an annotated texture dataset for supervised learning
ETH Zürich - Robotics, Systems and Control MSc Semester Project

This semester project tackled the exploration of a database of parametric textures. Its main objective was
to generate sufficiently many different combinations of the textures’ parameters (referred to as variants),
to be later used as training data for a supervised deep learning method tasked with recognising textures
in real images. To this end, a database of textures provided under the Substance format was analysed in
terms of the distribution of output channels (texture layers) and editable parameters for each texture. 

The set of these channels and parameters was then narrowed down in a principled manner, favouring those
that produced variants closest to what one would expect a texture recognition algorithm to encounter.
After generating the variants, the pair-wise Mean Squared Error (MSE) was employed as an appropriate
metric by which redundant, near-identical variants could be eliminated. Lastly, through random forest
regression, the relationship between variants’ parameters and their MSE was learned, creating a model
that can prune a set of generated variants to a concise form, fit for training a deep learning model.
