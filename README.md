
# Build your dream team with Autogen
   
This repo helps you to build a team of AI agents, this code is setting up a system of agents using the autogen library. The agents include a human admin, an AI Developer, a planner, an executor, and a quality assurance agent.
Each agent is configured with a name, a role, and specific behaviors or responsibilities.   

![image](https://github.com/user-attachments/assets/4585c332-f1a1-4519-a590-6b76a7f8e72e)

   
# Installation  
   
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
pip install -r requirements.txt
```
2. Update credentials

> Check [here](https://github.com/microsoft/autogen/blob/main/OAI_CONFIG_LIST_sample)
   - Update the file with your credentials
   - Save it as OAI_CONFIG_LIST
## Run
You can run the Python notebook build-dream-team.ipynb or run the app with Streamlit
```bash
streamlit run app.py
```



  
