from typing import List, Dict, Any, Optional
from swarms import Agent
from swarms.utils.loguru_logger import logger

class DFSSwarm:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.visited: set = set()
        self.results: List[Dict[str, Any]] = [] # Store results as dictionaries
        self.agent_tasks = {}


    def dfs(self, agent: Agent, task: str, depth: int = 0) -> None:
        logger.info(f"{'  '*depth}DFS: Agent {agent.agent_name} processing task: {task}")

        if (agent.agent_name, task) in self.visited: # Check for cycles
            logger.warning(f"{'  '*depth}DFS: Cycle detected, skipping task: {task} for agent {agent.agent_name}")
            return

        self.visited.add((agent.agent_name, task))

        try:
            result = agent.run(task)
            self.results.append({"agent": agent.agent_name, "task": task, "result": result, "depth": depth})

            if isinstance(result, dict) and "next_tasks" in result and result["next_tasks"]:
                next_tasks = result["next_tasks"]
                if not isinstance(next_tasks, list): # Handle cases where next_tasks might not be a list
                    next_tasks = [next_tasks] # Make it a list if not already


                for next_task in next_tasks:
                    next_agent = self._get_next_agent(agent, next_task)
                    if next_agent:
                        self.dfs(next_agent, next_task, depth + 1) # Recursive call
                    else:
                        logger.warning(f"{'  '*depth}DFS: No available agent for task: {next_task}")
                        self.results.append({"agent": "None", "task": next_task, "result": "No agent available", "depth": depth+1})


        except Exception as e:
            logger.error(f"{'  '*depth}DFS: Agent {agent.agent_name} encountered an error: {e}")
            self.results.append({"agent": agent.agent_name, "task": task, "result": f"Error: {e}", "depth": depth})

    def _get_next_agent(self, current_agent: Agent, next_task: str) -> Optional[Agent]:

        # Implement agent selection logic here (Examples below)

        # 1. Round Robin (excluding current agent)
        available_agents = [agent for agent in self.agents if agent != current_agent and agent.agent_name not in self.agent_tasks]
        if available_agents:
            next_agent = available_agents[0]
            self.agent_tasks[next_agent.agent_name] = next_task # Assign agent to the task
            return next_agent

        #  2. Task based selection (placeholder - replace with your logic)
        # for agent in self.agents:
        #     if agent != current_agent and agent.is_suitable_for_task(next_task): # Implement is_suitable_for_task in your Agent class
        #         return agent

        return None


    def run(self, initial_task: str) -> List[Dict[str, Any]]:
        if not self.agents:
            logger.warning("DFS: No agents in the swarm.")
            return []
        initial_agent = self.agents[0]
        self.dfs(initial_agent, initial_task)
        return self.results
