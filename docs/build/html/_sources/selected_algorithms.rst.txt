Solution Approach
=====

Framework
----------------

By viewing an initial data set containing component characteristics in conjunction with their determined control plan features (further referred to as output features), we have determined that all desired output features (testing equipment, sampling rate, validation procedure) are selected from a finite catalogue of options which is greater than 2.
Following this discovery we have hypothesized the specific problem to solve to be a multi-class classification problem, and that it may be possible to predict the desired output features using suitable machine learning algorithms with high accuracy after training them on the vast amount of historical data for existing components which Jopp possesses.

Initial Testing
----------------

During initial testing with multiple machine learning algorithms suitable for a multi-class classification problem, we have discovered that the desired output features are predictable with a significant accuracy by using a combination of significant input features, determined to be the characteristic name, its optimal measurement, its lower and upper measurement limits, its measurement unit, its process category, and the machine that the characteristic is created with.

Further, we have determined the best performing algorithms with the specific data set applied to be Random Forest, K-Nearest Neighbors, Support Vector Machine as well as Multi-Layer Perceptron, with each algorihm performing comparatively differently for each of the three desired output features.

While significant predictive power could be achieved for each desired output feature, it has also been discovered that there is a margin of error when using machine learning in order to predict the mentioned features. Due to the data used in training being a real-world data set which has been built up manually over time there are inconsistencies as well as errors contained within, impacting the achievable predictive power.

Tool Design
----------------

Due to the above mentioned discoveries, we have designed our tool to provide the following core functionality: A web-UI centered around delivering decision support, in which a set of component characteristics data is input which is then relayed to a disctinct pre-trained model optimized to predict a specific output feature using the best-performing algorithm for that feature.
After completion of predictions, the results are displayed to the user through the web-UI, where the user can validate and manipulate the results in order to account for the non-perfect accuracy in predictions. A probability value displayed for each output feature that shows the confidence of the trained models in predicting that feature is displayed in order to assist during this phase.
Further, to achieve a self-reinforcement loop, new data tuples gathered in this way are saved and can be used to re-train models, improving their predictive power over time. A monitoring page displaying metrics regarding the current as well as previous model generations assures long-term quality control of our tool.