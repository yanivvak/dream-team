[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/yaniv-vaknin-7a8324178/)
# Build your dream team with Autogen
   
This repo helps you to build a team of AI agents, this code is setting up a system of agents using the autogen library. The agents include a human admin, an AI Developer, a planner, an executor, and a quality assurance agent.
Each agent is configured with a name, a role, and specific behaviors or responsibilities.   

![image](https://github.com/user-attachments/assets/4585c332-f1a1-4519-a590-6b76a7f8e72e)

:tada: November 18, 2024: we are porting this repo to  [Autogen 0.4](https://microsoft.github.io/autogen/0.4.0.dev6/index.html), A new event driven, asynchronous architecture for AutoGen and [Magentic One](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-magentic-one)
   
# Installation
   
## Clone the repository     
```bash  
git clone https://github.com/yanivvak/dream-team.git  
```

## Deploy Azure Resources and the app

```bash
azd up
```

## Navigate to the project directory  
```bash  
cd src 
```

Set up a virtual environment (Preferred)
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
> More information about virtual environments can be found [here](https://docs.python.org/3/tutorial/venv.html)

 
## Install dependencies
```bash
pip install -r requirements.txt
```
```bash
git clone --depth 1 https://github.com/microsoft/autogen.git 
cd autogen/python/packages/autogen-magentic-one
pip install -e .
```

```bash
playwright install --with-deps chromium
```

## Update configuration

   - If you used AZD to deploy the resources just run `azd env get-values > .env` in the `src` directory
   - Alternatively, copy `.env.sample` (under src) into `.env`

> Magentic-One code uses code execution, you need to have Docker installed to run the examples if you use local execution

# Run
```bash
streamlit run app.py
```

  
