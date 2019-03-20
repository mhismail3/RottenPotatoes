# Rotten Potatoes
### By: Mohsin Ismail and Nivethan Sethupathi
### DSC478 (Winter 2019) Final Project

This project is a movie recommendation engine based on similar keywords and user ratings.


- TO RUN AS A STANDALONE APP

    You can find the completed application at the following link: [Project App Link](http://rottenpotatoes2-env.5qt2cegbay.us-east-2.elasticbeanstalk.com/)
    
- TO RUN THE ENGINE SOURCE CODE IN YOUR PYTHON IDE

    All of our project source code and files can be found on the project's Github page at the following link: [Github Link](https://github.com/nsethupathi/RottenPotatoes)
    
    Please have the Engine.py and Data.py files, as well as the "data" folder containing the relevant .csv files, in your current directory.
    
    Make sure you have installed the libraries specified in the "requirements.txt" file
    
    In your IDE, run
    
    ```python
    import Engine
    e = Engine.Engine()
    e.get_recommendations(title, number, option)
    ```
    
    replacing "title" with the title of a movie as a string, "number" with an integer
    representing how many movies to receive from the engine, and "option" being either
    "keywords" or "ratings" representing the metric to use in the algorithm.
    
    
    #### Note:
    We deployed this application online using AWS engine and services, which was a daunting process.
    If you would like more information on how to build/deploy this app yourself, please reach out to us.