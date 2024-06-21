# NaCo-Ants

This project contains three main folders, each focusing on different aspects of simulating and optimizing ant colony behaviors.

## Folders and Files

### 1. PyNants

- **nants_5sens.py**
  - Running this file will start up and run 100 simulations, returning the average amount of food collected per simulation.

### 2. old_versionV1: Searching Nest Version

- **EA**
  - Running this file will start up the evolutionary algorithm. You can edit the parameters at line 233 to customize the simulation.

- **Environment**
  - Uncomment the last two lines of code in this file to see a running simulation that continues indefinitely.

### 3. Version V2: Food Foraging Version

- **Collective EA**
  - Running this Evolutionary Algorithm initiates 10 generations of 10 populations of 50 ants each. Note that this process can be quite slow.

- **Environment**
  - Uncomment the last two lines of code in this file to view the simulation running indefinitely.

## Usage Instructions

1. **PyNants**: 
   - Navigate to the `PyNants` folder and run `nants_5sens.py` to execute 100 simulations and obtain the average food per simulation.

2. **old_versionV1**: 
   - Navigate to the `EA` folder and run the file to start the evolutionary algorithm. Adjust parameters at line 233 as needed.
   - In the `Environment` folder, uncomment the last two lines of the file to observe an indefinite simulation.

3. **Version V2**:
   - Navigate to the `Collective EA` folder and run the file to start the evolutionary algorithm for food foraging. This will execute 10 generations with 10 populations of 50 ants each.
   - In the `Environment` folder, uncomment the last two lines to see the simulation run indefinitely.
