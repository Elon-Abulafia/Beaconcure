# Beaconcure
## Running the application
* Before running, change the path for the documents folder in the main file to be where you store your documents.
```bash
pip install -r requirements.txt
python main.py
```

## Design patterns used 
### Strategy
The strategy pattern was used in the validators section in order to allow for future validators to be added easily.

####  Pros:
- Flexibility: Strategies can be swapped during runtime, this allows us to swap between different validators dynamically.
- Reusability: The different classes can be reused multiple times in order to validate different types of data more generically.
- Encapsulation: Each validation algorithm is encapsulated within its own class, this allows for easy maintenance without harming other validation strategies.
#### Cons:
- Complexity: Makes the code a lot more complex than just implementing a different validation function for each use case.
- Over Engineering: This pattern might be a bit of an overkill in most situations and can just slow down the development process.


### Factory
The factory pattern was used in the data layer to manage the different DB managers of the system.
#### Pros:
- Reusability: The different implementations of DBManager can be used interchangeably in the future without adhering to specific db syntax.
- Encapsulation: The factory itself encapsulates the creation process of every DBManager making it much easier to debug and maintain.
- Simple Complex Object Creation: By controlling the creation process of the different DBManagers, the factory makes it easier to create the different managers. All that is needed is the database details to exist within the environment variables.

#### Cons:
- Increased Complexity: Compared to the Singleton pattern which could have been used here to maintain a single database connection at all times.
- More Potential Points of Failure: The factory can create a lot of connections to the different databases simultaneously, making it very dangerous to maintain minimal db connections when considering multi processing or multiple objects being created for a single task.


# Considerations
- Change the DBManager class to be a singleton to prevent multiple database connections at the same time.
- Replace the Strategy pattern with Chain of Responsibility to allow for bad data to not be pushed into the db in the first place.
- Find a better Design Pattern for the parser class instead of wrapping it generically with a base class.