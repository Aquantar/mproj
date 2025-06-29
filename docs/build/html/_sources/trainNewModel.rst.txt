trainNewModels
=====

This is a header
^^^^^^^^^^^^^^^^

This is a paragraph. It can span multiple lines, and you can continue writing more content here.
Just make sure to leave a blank line between paragraphs.

Here's a code snippet from your tool:

.. code-block:: python

    conversionMap = dict()
    for col in allCols:
        if col in trainData.columns:
            conversionOutput = convertTextColumnToNumbers(trainData, col)
            trainData = conversionOutput[0]
            trainData[col] = pd.to_numeric(trainData[col])
            conversionMap[col] = conversionOutput[1]
