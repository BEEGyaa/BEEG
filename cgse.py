import os
from crewai import Agent, Task, Crew, Process

from langchain.llms import Ollama
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

from langchain_core.documents import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.utilities import ApifyWrapper

from time import time

import re
import asyncio
import logging
import torch

time1 = time()

#handle api keys
#from keys import GOOGLE_API_KEY, GOOGLE_CSE_ID, APIFY_API_KEY
GOOGLE_API_KEY = "AIzaSyBa08OnSGtfHSMN7zdWwnc8cmL1eV1vlQY"
GOOGLE_CSE_ID = "23fb9d6a6d89a4fe3"
APIFY_API_TOKEN = "apify_api_xycMNDDijPZFSin02zi24jwKs0DExj16nUTF"

os.environ["GOOGLE_CSE_ID"] = f"{GOOGLE_CSE_ID}"
os.environ["GOOGLE_API_KEY"] = f"{GOOGLE_API_KEY}"
os.environ["APIFY_API_TOKEN"] = f"{APIFY_API_TOKEN}"

#instantiate utilities for tool abilities
search = GoogleSearchAPIWrapper(k=3)
apify = ApifyWrapper()

# Configure basic logging for tools testing...
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#gpu check
def check_and_log_gpu_usage():
    if torch.cuda.is_available():
        logging.info("GPU is being used.")
    else:
        logging.info("CPU is being used.")

#google search function and tool
def google_search_function(query):
    check_and_log_gpu_usage()
    logging.info(f"Searching for: {query}")
    return search.results(query, num_results=3)  # You can adjust the number of results as needed

google_search = Tool(
    name="Google Search",
    description="Search Google for recent relevant results.",
    func=google_search_function,
)

#scraper function and tool
def scrape_with_apify(url):
    check_and_log_gpu_usage()
    logging.info(f"Starting to scrape URL: {url}")

    # Strip unwanted characters around the URL
    match = re.search(r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+', url)
    if match:
        url = match.group()
        logging.info(f"URL after regex match: {url}")
    else:
        logging.warning(f"No valid URL found in the provided string: {url}")
        return None

    run_input = {"startUrls": [{"url": url}]}
    logging.info(f"Run input for Apify: {run_input}")

    try:
        loader = apify.call_actor(
            actor_id="apify/website-content-crawler",
            run_input=run_input,
            dataset_mapping_function=lambda item: Document(
                page_content=item["text"] or "", metadata={"source": item["url"]}
            ),
        )
        logging.info(f"Apify actor called successfully for URL: {url}")

        # Load the documents directly
        documents = loader.load()
        logging.info(f"Documents loaded for URL: {url}")

        return documents
    except Exception as e:
        logging.error(f"Error during scraping URL {url}: {e}")
        return None




#now the tool itself
apify_scraping_tool = Tool(
    name="Apify Web Scraper",
    description="Scrapes content from pages at specified URLs using Apify",
    func=scrape_with_apify
)

ollama_orca2 = Ollama(model="orca2")
ollama_mistral = Ollama(model="mistral:instruct")
ollama_dolphin = Ollama(model="dolphin2.2-mistral")

# Define your agents with roles and goals
researcher = Agent(
  role='Google Researcher',
  goal='Use Tool: Google Search to retrieve a list of dictionaries. Pass on the list as your Final Answer to complete your task.',
  backstory="Use google search to search for the specified topic. Once you've received a list of results, judge your work complete and pass on the received results as your Final Answer.",
  verbose=True,
  allow_delegation=False,
  post_tool_text="Now give a Final Answer, formatted so: Final Answer: <list of results from Google Search>",
  llm=ollama_mistral,
  # Ollama model passed here
  tools=[google_search]
)

research_director = Agent(
  role='Director of research',
  goal='Choose a quality source of engaging information. Choose an interesting title from the list provided, then pass on the URL of the corresponding website',
  backstory="Once you've selected an interesting news story by its title, pass on the URL by giving a Final Answer that contains only the desired URL, with no quotes or brackets, like <>, around it.",
  verbose=True,
  allow_delegation=False,
  llm=ollama_mistral, # Ollama model passed here
)

typist = Agent(
  role='Typist',
  goal='Use the Apify Web Scraper tool and input the URL provided, then output the results as your Final Answer.',
  backstory="Scrape the URL's content with the Apify Web Scraper, inputting the URL that was passed to you. Then give a Final Answer containing the scraped text.",
  verbose=True,
  allow_delegation=False,
  post_tool_text="Now give a Final Answer, formatted so: Final Answer: <Scraped text>",
  llm=ollama_mistral, # Ollama model passed here
  tools=[apify_scraping_tool]
)

writer = Agent(
  role='Writer',
  goal='Create engaging content',
  backstory="You're a skilled writer.",
  verbose=True,
  allow_delegation=False,
  llm=ollama_mistral, # Ollama model passed here
)

# Create tasks for your agents
task1 = Task(description='Google "2023 + China navy + South China Sea," using the Google Search tool. Your Final Answer will be the list of Google Search results and nothing else.', agent=researcher)
task2 = Task(description='Choose the most important and interesting article by title. Think: "The most interesting title is," choose one. Take the corresponding URL from the dict. Your Final Answer should be one URL alone.', agent=research_director)
task3 = Task(description='Use the Apify Web Scraper tool to extract content from the provided URL. The URL should be your Action Input. Once the site has been scraped, give a Final Answer consisting of the resulting text.', agent=typist)
task4 = Task(description='Write a blog post on current news about China based on the provided information', agent=writer)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, research_director, writer],
  tasks=[task1, task2, task3, task4],
  verbose=True, # Crew verbose more will let you know what tasks are being worked on
  process=Process.sequential # Sequential process will have tasks executed one after the other and the outcome of the previous one is passed as extra content into this next.
)

# check GPU and get your crew to work!
check_and_log_gpu_usage()
result = crew.kickoff()

time2 = (time() - time1)
print(time2)