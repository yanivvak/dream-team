
# Build your dream team with Autogen
   
This repo helps you to build a team of AI agents, this code is setting up a system of agents using the autogen library. The agents include a human admin, an AI Developer, a planner, an executor, and a quality assurance agent.
Each agent is configured with a name, a role, and specific behaviors or responsibilities.   
   
   
## Installation  
   
## Clone the repository     
```bash  
git clone https://github.com/yanivvak/dream-team.git  
```
## Navigate to the project directory  
```bash  
cd dream-team  
```

1. Set up a virtual environment (Preferred)
```bash
python -m venv dream
```
Once you’ve created a virtual environment, you may activate it.

On Windows, run:
```bash
dream\Scripts\activate
```
On Unix or MacOS, run:
```bash
source dream/bin/activate
```
To deactivate :
```bash
deactivate
```
> More information about virtual environments can be found [here] (https://docs.python.org/3/tutorial/venv.html)

 
## Install dependencies
```bash
pip install pyautogen
```
2. Update credentials

> Check [here](https://github.com/microsoft/autogen/blob/main/OAI_CONFIG_LIST_sample)
   - Update the file with your credentials
   - Save it as OAI_CONFIG_LIST.json
   
## Contributing  
   
Guidelines for contributing to the project.  
   
1. Fork the repository.  
2. Create a new branch (`git checkout -b feature-branch`).  
3. Make your changes.  
4. Commit your changes (`git commit -m 'Add some feature'`).  
5. Push to the branch (`git push origin feature-branch`).  
6. Open a pull request.

  
